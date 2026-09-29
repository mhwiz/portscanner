## Python Port Scanner

My most enjoyable project to date. I built a multi-threaded port scanner while also adding some additional spice:

- **Network interface selection**
  Lists available interfaces and lets the user choose from the results. This supports external adapters (ALFA cards in monitor/injection mode) that are typically used in tandem with these types of programs/techniques.

- **Input validation**
  Keeps the user flow linear and reduces errors before scanning begins.

- **Targeted benchmarking**
  Wraps only the scanning function in a timing call (`time.perf_counter`) rather than measuring the entire program. This was my favorite addition to the script.   
