Make sure you’ve installed `virtualenv`, and you’ve cloned both the `writer` and the `I-like-tight-pants-and-mathematics` repositories. The two folders should be placed next to each other. Then, from `writer`:

    virtualenv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    cp write/local_settings.example.py write/local_settings.py

Inbetween these steps, you need a `write.db` in the folder `write`. Copy the live one with `fab mirror` (from this checkout, after `local_settings.py` can reach the server). Then:

    python manage.py runserver

Then, you can visit `http://localhost:8000/and/` to see the generated files. `http://localhost:8000/is/` shows a preview of the files that will be generated, and `http://localhost:8000/or/` allows you to visit the editing interface.
