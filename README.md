\## AI Resume Shortlister



An end-to-end system that evaluates PDF resumes against a job description using Google's Gemini API. It includes:

\- A CLI to analyze local resumes and print a rich summary

\- A Student Portal for authenticated PDF uploads

\- An HR Dashboard to run AI analysis and manage shortlist decisions



\### Features

\- AI-powered, structured evaluation with per-criterion scores and reasoning

\- Rich console UI for quick local runs (`main.py`)

\- Two Flask apps:

&nbsp; - `student\_server.py`: upload PDFs, view upload history

&nbsp; - `hr\_server.py`: run analysis, view candidates, shortlist/reject

\- Persistent storage with SQLite (`instance/resume\_shortlister.db`)

\- Results saved to `results/analysis\_results.json`



\### Requirements

\- Python 3.8+

\- A Google Gemini API key



\### Quick Start

1\) Install dependencies

```bash

python -m pip install -e .

```



2\) Create `.env.local` with your Gemini API key

```bash

echo GEMINI\_API\_KEY=your-gemini-api-key > .env.local

```



3\) Provide inputs used by the evaluator

\- `guidance\_prompt.md` (evaluation rubric/instructions)

\- `job\_description.md` (the role to evaluate against)

\- Drop your PDF resumes into the `resumes/` folder



4\) Option A: Run the CLI analyzer

```bash

python main.py

```

This scans `resumes/`, sends them with the prompt and JD to Gemini, and prints a rich table plus summary panels. Results are also saved in `results/analysis\_results.json`.



5\) Option B: Start the full system (both web apps)

```bash

python start\_system.py

```

\- Student Portal: `http://localhost:5000`

\- HR Dashboard: `http://localhost:5001`



\### Running servers individually

\- Student portal only:

```bash

python student\_server.py

```



\- HR dashboard only:

```bash

python hr\_server.py

```



On first run, tables are created automatically; the student server seeds a sample job posting.



\### Configuration and Environment

\- `utils.setup\_environment()` loads `.env.local` and validates `GEMINI\_API\_KEY`.

\- Set `GEMINI\_API\_KEY` to a valid key. If missing or placeholder, runs will fail.

\- The Gemini model used by default is `gemini-1.5-flash` with tuned generation config.



\### Data and Outputs

\- Resumes: `resumes/\*.pdf`

\- Console run output: printed to terminal

\- Analysis JSON: `results/analysis\_results.json`

\- Database (web apps): `instance/resume\_shortlister.db`



\### Project Structure (high-level)

\- `main.py`: CLI analysis flow

\- `start\_system.py`: installs deps, checks required files, starts both servers

\- `student\_server.py`: uploads, student dashboard, auth

\- `hr\_server.py`: analysis, HR dashboard, auth

\- `utils.py`: Gemini integration, file loading, evaluation models

\- `ui.py`: rich console rendering utilities

\- `models.py`, `auth\_utils.py`, `auth\_routes.py`: persistence and authentication

\- `resumes/`: place PDF resumes here

\- `results/analysis\_results.json`: saved results

\- `assets/`: images used in docs/UIs



\### Common Errors \& Troubleshooting

\- Missing `.env.local` or `GEMINI\_API\_KEY`:

&nbsp; - Create `.env.local` and set a valid key.

\- No PDFs found:

&nbsp; - Put at least one `.pdf` into `resumes/`.

\- Missing templates:

&nbsp; - Ensure `guidance\_prompt.md` and `job\_description.md` exist and are populated.

\- Gemini response parse error:

&nbsp; - Re-run; ensure prompt/JD are reasonable and the API key has access.



\### License

See `LICENSE` for details.



