from quart import (
    Quart, request, render_template, abort
)
from pathlib import Path
import os
import markdown

app = Quart(__name__)

app.config.from_prefixed_env()

DIRECTORY = Path(app.config.get("UPLOADS", None) or "./uploads")
DIRECTORY.mkdir(parents=True, exist_ok=True)

@app.route("/")
async def index():
    return "TODO: Render index.html"

def get_article_path(topic: str, article: str) -> str:
    return DIRECTORY / topic / article

def get_etag(filepath: Path, *, abort: bool = False):
    try:
        stat = os.stat(filepath)
    except FileNotFoundError:
        return abort(404) if abort else None
    return hex(stat.st_mtime_ns)

def assert_etag(etag: str):
    if "If-Match" in request.headers and request.headers["If-Match"] != etag: abort(412)
    if "If-None-Match" in request.headers and request.headers["If-None-Match"] != etag: abort(304)

@app.route("/<topic>/<article>", methods=["PUT", "GET"])
async def article(topic: str, article: str):
    filepath = get_article_path(topic, article)
    etag = get_etag(filepath, abort=request.method == "GET")
    assert_etag(etag)
    mode = "r" if request.method == "GET" else "w"
    if etag is None and not filepath.parent.exists():
        filepath.parent.mkdir()
    with open(filepath, mode) as file:
        if request.method == "PUT":
            async for chunk in request.body:
                file.write(chunk.decode())
            return "", 204
        content = markdown.markdown(file.read())
    return await render_template("article.html", content=content) 

@app.route("/editor/<topic>/<article>")
async def editor(topic: str, article: str):
    with open(get_article_path(topic, article), "r") as fp:
        content = fp.read()
    return await render_template("editor.html", content=content)
    
        
    
    

