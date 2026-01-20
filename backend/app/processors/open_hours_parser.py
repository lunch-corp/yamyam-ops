"""
Kakao 음식점 영업시간 파싱 모듈
"""

import ast
import re
from datetime import time
from typing import Any


def parse_korean_day_to_int(day_desc: str) -> int | None:
    """
    한글 요일을 정수로 변환

    Args:
        day_desc: '토(12/6)', '일(12/7)' 등의 형식

    Returns:
        0=월요일, 1=화요일, ..., 6=일요일, None=파싱 실패
    """
    day_mapping = {
        "월": 0,
        "화": 1,
        "수": 2,
        "목": 3,
        "금": 4,
        "토": 5,
        "일": 6,
    }

    # '토(12/6)' 형식에서 '토' 추출
    if "(" in day_desc:
        korean_day = day_desc.split("(")[0].strip()
    else:
        korean_day = day_desc.strip()

    return day_mapping.get(korean_day)


def parse_time_string(time_str: str) -> tuple[time | None, time | None]:
    """
    시간 문자열을 파싱

    Args:
        time_str: '10:00 ~ 20:00', '08:00 ~ 16:00' 등의 형식

    Returns:
        (start_time, end_time) 튜플, 파싱 실패 시 (None, None)
    """
    try:
        # '10:00 ~ 20:00' 형식 파싱
        if "~" in time_str:
            parts = time_str.split("~")
            if len(parts) == 2:
                start_str = parts[0].strip()
                end_str = parts[1].strip()

                # '10:00' 형식을 time 객체로 변환
                start_match = re.match(r"(\d{1,2}):(\d{2})", start_str)
                end_match = re.match(r"(\d{1,2}):(\d{2})", end_str)

                if start_match and end_match:
                    start_hour = int(start_match.group(1))
                    start_minute = int(start_match.group(2))
                    end_hour = int(end_match.group(1))
                    end_minute = int(end_match.group(2))

                    # 24시간 형식 검증
                    if 0 <= start_hour < 24 and 0 <= start_minute < 60:
                        if 0 <= end_hour < 24 and 0 <= end_minute < 60:
                            return (
                                time(start_hour, start_minute),
                                time(end_hour, end_minute),
                            )
    except Exception:
        pass

    return None, None


def parse_open_hours(diner_idx: int, open_hours_data: Any) -> list[dict]:
    """
    open_hours 데이터를 파싱하여 요일별 영업시간 정보 추출

    Args:
        diner_idx: 음식점 고유 인덱스
        open_hours_data: open_hours 컬럼 데이터 (문자열 또는 리스트)

    Returns:
        [{
            'diner_idx': int,
            'day_of_week': int,
            'is_open': bool,
            'start_time': str | None,  # 'HH:MM:SS' 형식
            'end_time': str | None,    # 'HH:MM:SS' 형식
            'description': str | None
        }, ...]
    """
    results = []

    # None 또는 NaN 체크
    if open_hours_data is None or (
        isinstance(open_hours_data, float) and open_hours_data != open_hours_data
    ):
        return results

    try:
        # 문자열인 경우 파싱
        if isinstance(open_hours_data, str):
            parsed = ast.literal_eval(open_hours_data)
        else:
            parsed = open_hours_data

        # 리스트가 아니면 리스트로 변환
        if not isinstance(parsed, list):
            parsed = [parsed]

        # 빈 리스트 체크
        if len(parsed) == 0:
            return results

        # 첫 번째 항목만 사용 (보통 카카오맵 정보)
        item = parsed[0]

        # week_from_today 구조 확인
        if "week_from_today" not in item:
            return results

        week_from_today = item["week_from_today"]
        if "week_periods" not in week_from_today:
            return results

        week_periods = week_from_today["week_periods"]

        # week_periods 순회
        for period in week_periods:
            if "days" not in period:
                continue

            for day in period["days"]:
                day_desc = day.get("day_of_the_week_desc", "")

                # 요일 파싱
                day_of_week = parse_korean_day_to_int(day_desc)
                if day_of_week is None:
                    continue

                # 영업일 처리
                if "on_days" in day and "start_end_time_desc" in day["on_days"]:
                    time_str = day["on_days"]["start_end_time_desc"]
                    start_time, end_time = parse_time_string(time_str)

                    # time 객체를 문자열로 변환
                    start_time_str = (
                        start_time.strftime("%H:%M:%S") if start_time else None
                    )
                    end_time_str = end_time.strftime("%H:%M:%S") if end_time else None

                    results.append(
                        {
                            "diner_idx": diner_idx,
                            "day_of_week": day_of_week,
                            "is_open": True,
                            "start_time": start_time_str,
                            "end_time": end_time_str,
                            "description": time_str if start_time is None else None,
                        }
                    )

                # 휴무일 처리
                elif "off_days_desc" in day:
                    off_desc = day["off_days_desc"]
                    results.append(
                        {
                            "diner_idx": diner_idx,
                            "day_of_week": day_of_week,
                            "is_open": False,
                            "start_time": None,
                            "end_time": None,
                            "description": off_desc,
                        }
                    )

    except Exception:
        # 파싱 실패 시 빈 리스트 반환
        pass

    return results


def parse_open_hours_batch(diner_df) -> list[dict]:
    """
    DataFrame의 open_hours 컬럼을 배치로 파싱

    Args:
        diner_df: diner DataFrame (diner_idx, open_hours 컬럼 필요)

    Returns:
        파싱된 영업시간 정보 리스트
    """
    all_results = []

    for _, row in diner_df.iterrows():
        diner_idx = row["diner_idx"]
        open_hours_data = row.get("open_hours")

        parsed_hours = parse_open_hours(diner_idx, open_hours_data)
        all_results.extend(parsed_hours)

    return all_results
