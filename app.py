```python
from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ニコニコ動画検索</title>
<style>
body {
  background: #171717;
  color: white;
  font-family: sans-serif;
  padding: 20px;
  max-width: 1000px;
  margin: auto;
}
h1 { color: #ff7777; }
input {
  box-sizing: border-box;
  width: 75%;
  padding: 12px;
}
button {
  padding: 12px;
  background: #e83939;
  color: white;
  border: 0;
  cursor: pointer;
}
.results {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 15px;
}
.card {
  background: #292929;
  padding: 12px;
  border-radius: 8px;
}
.card img { width: 100%; }
.player {
  width: 100%;
  aspect-ratio: 16 / 9;
  margin: 20px 0;
}
iframe { width: 100%; height: 100%; border: 0; }
a { color: #ffaaaa; }
</style>
</head>
<body>
<h1>ニコニコ動画検索</h1>

<form method="get">
  <input name="q" value="{{ q }}" placeholder="検索キーワード">
  <button type="submit">検索</button>
</form>

<div class="player" id="player">
  <iframe id="frame"
    src="https://embed.nicovideo.jp/watch/sm9"
    title="動画プレーヤー" allowfullscreen>
  </iframe>
</div>

<h2>検索結果</h2>
<div class="results">
{% for v in videos %}
  <div class="card">
    {% if v.thumbnailUrl %}
      <img src="{{ v.thumbnailUrl }}" alt="動画サムネイル">
    {% endif %}
    <h3>{{ v.title }}</h3>
    <p>{{ v.contentId }}</p>
    <button type="button"
      onclick="playVideo('{{ v.contentId }}')">
      ページ内で再生
    </button>
    <p><a href="https://www.nicovideo.jp/watch/{{ v.contentId }}"
      target="_blank" rel="noopener noreferrer">公式ページ</a></p>
  </div>
{% endfor %}
</div>

<script>
function playVideo(id) {
  document.getElementById("frame").src =
    "https://embed.nicovideo.jp/watch/" +
    encodeURIComponent(id);
  document.getElementById("player")
    .scrollIntoView({behavior: "smooth"});
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    videos = []
    error = ""

    if q:
        try:
            response = requests.get(
                "https://snapshot.search.nicovideo.jp/"
                "api/v2/snapshot/video/contents/search",
                params={
                    "q": q,
                    "targets": "title",
                    "fields": "contentId,title,thumbnailUrl",
                    "_sort": "-viewCounter",
                    "_limit": 20,
                    "_context": "MyNiconicoSearch"
                },
                timeout=15
            )
            response.raise_for_status()
            videos = response.json().get("data", [])
        except (requests.RequestException, ValueError):
            error = "検索に失敗しました。時間をおいて再度試してください。"

    return render_template_string(
        HTML, q=q, videos=videos, error=error
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
```
