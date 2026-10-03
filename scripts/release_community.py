"""Create the explicitly scoped roadmap milestone and labels with normal Actions permissions."""

import json
import os
import urllib.error
import urllib.request

REPOSITORY = "Prajwal-Pratap-Yadav/Image-Steganography-in-Python"


def write_ok():
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise SystemExit("Repository scope mismatch")


def request(path, method="GET", body=None):
    write_ok()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}/{path}",
        data=data,
        method=method,
        headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def main():
    write_ok()
    labels = {label["name"] for label in request("labels?per_page=100")}
    for name, color, description in (
        ("evidence", "38bdf8", "Measured reproduction or evaluation"),
        ("format", "a78bfa", "Payload format and interoperability"),
    ):
        if name not in labels:
            request("labels", "POST", {"name": name, "color": color, "description": description})
    title = "v0.2.0 — interoperability and natural-image evaluation"
    milestones = request("milestones?state=all&per_page=100")
    milestone = next((m for m in milestones if m["title"] == title), None)
    if milestone is None:
        milestone = request(
            "milestones",
            "POST",
            {
                "title": title,
                "description": "Format vectors, licensed corpus evaluation and Windows coverage.",
            },
        )
    for number in (1, 2, 3):
        request(f"issues/{number}", "PATCH", {"milestone": milestone["number"]})
    print(milestone["html_url"])


if __name__ == "__main__":
    main()
