import os
import time
import json
from datetime import datetime, date
import requests
import pandas as pd
from tqdm import tqdm

from src.utils import config

class TMDBCollector:
    def __init__(self, api_key):
        """
        api_key: TMDB 개인 API Key
        """
        self.api_key = '34001fe64b18a059b394f98a65974226'
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()  # HTTP 세션 재사용 (속도 및 연결 효율 개선)

        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)

    def _make_request(self, url, params):
        """
        TMDB API 호출 및 예외처리(최대 3회 재시도)  
        - TMDB API 호출에 실패할 경우, 1초 대기 후 최대 3회까지 재시도
        - 성공하면 json 반환, 실패하면 None 반환
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                r = self.session.get(url, params=params)
                r.raise_for_status()
                time.sleep(0.25)  # TMDB API Rate Limit(초당 4회) 대응
                return r.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"[ERR] {url} after {max_retries} tries:", e)
                time.sleep(1)  # 실패시 1초 쉬고 재시도
        return None

    def discover_movies_period(self, start_date, end_date, page=1):
        """
        특정 기간(예: 2020-01-01 ~ 2020-12-31)에 개봉한 영화 목록을 가져옴 (페이지네이션 지원)
        - page: 페이지 번호 (TMDB는 한 번에 20개 반환, 최대 500페이지=1만개 제한)
        """
        url = f"{self.base_url}/discover/movie"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR',
            'sort_by': 'popularity.desc',  # 인기순 정렬
            'page': page,                  # 요청할 페이지 번호
            'include_adult': 'false',      # 성인영화 제외
            'primary_release_date.gte': start_date,  # 시작일
            'primary_release_date.lte': end_date,    # 종료일
        }
        return self._make_request(url, params)

    def get_movie_details(self, movie_id):
        """
        영화 개별 상세정보(+ credits, keywords, similar, images, videos 등 부가 데이터 포함)를 반환
        """
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'ko-KR',
            'append_to_response': 'credits,keywords,similar,images,videos'  # 부가정보 추가
        }
        return self._make_request(url, params)

def collect_all_movies(collector, start_year, end_year, max_per_year=10000):
    """
    전체 연도 구간별로 영화 ID만 수집 (중복 제거)
    - max_per_year: 연도별 최대 수집 수(예: 10,000이면 한 해 만개까지만)
      → TMDB API는 한 요청에 20개씩, 한 연도 최대 500페이지까지(=10,000개)만 반환됨
    - 진행상황(progress) 파일로 중간 저장하여, 도중에 중단돼도 이어서 수집 가능
    """
    progress_file = os.path.join(config.RAW_DATA_DIR, 'ids_progress2.json')
    # 기존에 진행된 수집 내역 있으면 이어서(재시작 지원)
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            prog = json.load(f)
            year = prog['current_year']  # 이어서 수집할 연도
            all_ids = set(prog['collected_ids2'])
            print(f"▶ 이어서 {year}년부터 수집")
    else:
        year = start_year
        all_ids = set()

    for y in range(year, end_year+1):
        print(f"\n▶ {y}년 영화 ID 수집 (최대 {max_per_year}개 제한)")
        page = 1
        # 첫 페이지 호출해서 전체 페이지 수 구하기
        first = collector.discover_movies_period(f"{y}-01-01", f"{y}-12-31", page)
        if not first:
            print(f"  → {y}년 수집 실패, 건너뜀")
            continue
        total = first.get('total_pages', 0)  # TMDB가 반환하는 총 페이지 수
        year_count = 0  # 해당 연도 누적 카운트
        # 페이지 루프(예: 최대 500페이지, 20*500=10,000개)
        for p in tqdm(range(1, total+1), desc=f"{y} pages"):
            res = collector.discover_movies_period(f"{y}-01-01", f"{y}-12-31", p)
            if not res or not res.get('results'):
                break
            for m in res['results']:
                if year_count >= max_per_year:
                    print(f"  → {y}년 {max_per_year}개 도달, 다음 연도로 넘어감")
                    break
                all_ids.add(m['id'])  # set이므로 중복 없음
                year_count += 1
            if year_count >= max_per_year:
                break
        # 중간 저장 (진행상황 & 백업)
        with open(progress_file, 'w') as f:
            json.dump({'current_year': y+1, 'collected_ids2': list(all_ids)}, f)
        with open(os.path.join(config.RAW_DATA_DIR, f'movie_ids_up_to_{y}.json'), 'w') as f:
            json.dump(list(all_ids), f)
        print(f"  → 누적 ID: {len(all_ids)}개 (이번 연도 {year_count}개)")
    return list(all_ids)

def collect_movie_details(collector, movie_ids):
    """
    영화 ID 리스트에 대해 상세정보를 모두 수집
    - 수집 중간 상태(진행 상황)를 progress 파일에 저장 → 중단/재시작 지원
    - 100개마다 임시 저장, 전체 완료 후에는 최종 CSV로 저장
    """
    progress_file = os.path.join(config.RAW_DATA_DIR, 'details_progress2.json')
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            prog = json.load(f)
            done_ids = set(prog['collected_ids2'])         # 이미 수집 완료된 ID
            details = prog['collected_movies2']             # 이미 저장된 상세 데이터
            print(f"▶ 이어서 상세 {len(done_ids)}개 완료된 상태")
    else:
        done_ids = set()
        details = []

    # 아직 상세정보를 안 받은 영화만 타겟팅
    to_collect = [mid for mid in movie_ids if mid not in done_ids]
    for mid in tqdm(to_collect, desc="fetch details", mininterval=100, miniters=1000):
        d = collector.get_movie_details(mid)
        if not d:
            continue
        # 주요 컬럼만 뽑아서 dict로 변환
        info = {
            'id': d['id'],
            'title': d.get('title'),                                       # 한글 제목
            'original_title': d.get('original_title'),                     # 원제목
            'overview': d.get('overview'),                                 # 줄거리(설명)
            'genres': [g['name'] for g in d.get('genres', [])],            # 장르 목록
            'keywords': [k['name'] for k in d.get('keywords', {}).get('keywords', [])],  # 키워드
            'cast': [c['name'] for c in d['credits']['cast'][:10]],        # 주요 배우 상위 10명
            'crew': [c['name'] for c in d['credits']['crew'] if c['job'] in ('Director','Writer')],  # 감독, 작가
            'release_date': d.get('release_date'),                         # 개봉일
            'runtime': d.get('runtime'),                                   # 상영시간(분)
            'vote_average': d.get('vote_average'),                         # 평점
            'vote_count': d.get('vote_count'),                             # 평점 투표수
            'popularity': d.get('popularity'),                             # 인기 지표
            'poster_path': d.get('poster_path'),                           # 포스터 이미지 경로
            'similar_ids': [m['id'] for m in d.get('similar', {}).get('results', [])]    # 비슷한 영화 ID
        }
        details.append(info)
        done_ids.add(mid)
        # 100개마다 임시 저장 (진행상황 json + temp csv)
        if len(details) % 100 == 0:
            pd.DataFrame(details).to_csv(os.path.join(config.RAW_DATA_DIR, 'movies_detailed2_temp.csv'), index=False)
            with open(progress_file, 'w') as f:
                json.dump({'collected_ids2': list(done_ids), 'collected_movies2': details}, f)
    # 마지막 전체 저장 (진행상황 json + 최종 csv)

    current_date = date.today().strftime("%Y%m%d")  # 250521142130
    dst = os.path.join(config.RAW_DATA_DIR, f"TMDB_{current_date}.csv")
    print(dst)
    pd.DataFrame(details).to_csv(dst, index=False)
    with open(progress_file, 'w') as f:
        json.dump({'collected_ids2': list(done_ids), 'collected_movies2': details}, f)
    return details, dst
