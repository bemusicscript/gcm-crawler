"""
crawler.py

Crawler for the Rhythm Game
"""
import re
import requests
from config import USERNAME, PASSWORD

def get_ongeki_data(username, password, user_idx=0):
    """ (str, str, str) -> dict

    Crawl ongeki data from the official website.

    >>> get_ongeki_data("stypr", "password")
    """
    host = "https://ongeki-net.com/ongeki-mobile"
    headers = {"User-Agent": "Mozilla/5.0"}
    result = {}
    r = requests.Session()

    # get token from login
    response = r.get(f"{host}/", headers=headers)
    response_token = re.findall(
        '<input type="hidden" name="token" value="(.*)" />',
        response.text
    )
    if not response_token:
        return False

    # authenticate and select user idx
    data = {
        "segaId": username,
        "password": password,
        "token": response_token
    }
    response = r.post(f"{host}/submit/", data, headers=headers)
    if response.url != f"{host}/aimeList/":
        return False
    response = r.get(f"{host}/aimeList/submit/?idx={user_idx}")

    # parse user information from Home
    if response.url != f"{host}/home/":
        return False
    user_title = re.findall(
        r"<div class=\"trophy_block .+\">\n.+<span>(.+)</span>\n.+</div>", response.text
    )
    user_nickname = re.findall(
        r"<div class=\"name_block\ .+\">\n.+<span>(.+)</span>\n.+</div>", response.text
    )
    user_level_reincarnation = re.findall(
        r"<div class=\"reincarnation_block\">\n.+<span>(.+)</span>\n.+</div>",
        response.text,
    )
    user_level = re.findall(
        r"<div class=\"lv_block\ .+\">\n.+<span>(.+)</span>\n.+</div>", response.text
    )
    user_ratings = re.findall(
        (
            '<div class="rating_field .+">\n.+'
            + '<span class=".+">(.+)</span>'
            + '<span class=".+">(.+)</span>'
        ),
        response.text,
    )
    user_bp = re.findall(
        r"<div class=\"battle_rank_block\">\n.+\n.+<div class=\".+\">(.+)</div>\n",
        response.text,
    )
    if user_level_reincarnation:
        user_level = user_level_reincarnation[0] + user_level[0]
    else:
        user_level = user_level[0]
    user_level = int(user_level.replace(",", ""))

    # parse latest 10 playlogs
    result["log"] = []
    response = r.get(f"{host}/record/playlog")
    user_log_raw = response.text.split('<div class="container3 t_l">')[1]
    user_log = user_log_raw.split('<div class="clearfix"></div>')[1:-1]
    for _log in user_log[:10]:
        _log_title = re.findall(
            '<div class="m_5 l_h_10 break">\n.+<img .+>(.+)\n.+</div>', _log
        )
        _log_difficulty = re.findall(
            f'<img src="{host}/img/diff_(.+).png" />',
            _log
        )
        _log_score_sign = re.findall(
            f'<img src="{host}/img/score_tr_(.+).png".+>',
            _log
        )
        _log_score = re.findall(
            '<td class="technical_score_block(.+)?">\n.+\n.+<div class=".+">(.+)</div>\n',
            _log,
        )
        _log_extra = re.findall(
            '<img src="(.*) />',
            _log.split('div class="clearfix p_t_5 t_l f_0">')[1]
        )
        result["log"].append(
            {
                "title": _log_title[0].strip(),
                "difficulty": _log_difficulty[0].upper(),
                "score_sign": _log_score_sign[0].upper(),
                "is_new_record": bool(_log_score[0][0]),
                "score": int(_log_score[0][1].strip().replace(",", "")),
                "extra": _log_extra,
            }
        )

    result["info"] = {
        "title": user_title[0],
        "nickname": user_nickname[0],
        "level": user_level,
        "current_rating": user_ratings[0][0],
        "max_rating": user_ratings[0][1],
        "battle_point": user_bp[0],
    }

    return result

if __name__ == "__main__":
    print(get_ongeki_data(USERNAME, PASSWORD))
