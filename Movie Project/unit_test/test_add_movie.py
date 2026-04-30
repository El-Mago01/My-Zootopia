import pytest
from main import shorten_string, command_add_movie, enter_movie_title


def test_add_movie_normal_1(monkeypatch: pytest.MonkeyPatch):
    def fake_enter_movie_title():
        return " Lord of Rings"
    
    monkeypatch.setattr("enter_movie_title", fake_enter_movie_title)
    command_add_movie()

    print(service)

    assert service == "Movie added successfully"


