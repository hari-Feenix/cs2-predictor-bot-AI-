import json
LEADERBOARD_DB = 'data/leaderboard.json'

def _load():
    try:
        with open(LEADERBOARD_DB, 'r') as f:
            return json.load(f)
    except:
        return {}

async def get_leaderboard(bot):
    leaderboard = _load()
    sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    lines = ["**🏆 Leaderboard:**"]
    for uid, score in sorted_lb[:10]:
        user = await bot.fetch_user(int(uid))
        lines.append(f"{user.name}: {score} pts")
    return '\n'.join(lines)
