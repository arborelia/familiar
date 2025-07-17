from flask import Flask
from familiar import db
from markupsafe import escape

app = Flask(__name__)

def pinball_data(table_id: str) -> str:
    rows = db.run("SELECT name, year, mfg, designer, vpx FROM pinballtables WHERE id=?", table_id.lower())
    if rows:
        table_name, year, mfg, designer, vpx = rows[0]
        hi_score_rows = db.run("SELECT username, score FROM scores WHERE table_id=? ORDER BY score DESC LIMIT 1", table_id)
        if hi_score_rows:
            hi_score_player, score = hi_score_rows[0]
            hi_score_line = f"{score:,} by {escape(hi_score_player)}"
        else:
            hi_score_line = "None yet"
        if vpx.startswith('!'):
            rest = vpx[1:]
            virtual_credit = f"Digital version by {escape(rest)}"
        else:
            virtual_credit = f"VPX by {escape(vpx)}"
        return f"""
<!doctype html>
<html>
<h1>{escape(table_name)}</h1>
<p class="subtitle">({escape(mfg)}, {year})</p>
<p>Designer: {escape(designer)}</p>
{virtual_credit}
<p class="scoreprompt">!score {escape(table_id)}</p>
<p>High score: {hi_score_line}</p>
</html>
        """

    else:
        return f"<html>Table {table_id!r} not found.</html>"


@app.route("/hiscores/<int:episode>")
def hi_scores(episode: int) -> str:
    rows = db.run("select t.name, t.mfg, t.year, s.username, s.score from pinballtables t, scores s where s.table_id = t.id and t.episode=? order by t.name asc, s.score desc", episode)
    lines = ["<!doctype html>", "<html>", f"<h1>Episode {episode} High Scores</h1>", "<ul>"]
    seen_tables = set()
    for row in rows:
        table_name, mfg, year, username, score = row
        if table_name not in seen_tables:
            lines.append(f"<li><strong class=\"table\">{table_name}</strong>: {score:,} by {escape(username)}</li>")
            seen_tables.add(table_name)
    lines.append("</ul>")
    lines.append("</html>")
    return "\n".join(lines)


@app.route("/")
def front_page():
    return "Hi, scores!"


@app.route("/pinball/<table_id>")
def show_pinball_data(table_id: str):
    return pinball_data(table_id)

