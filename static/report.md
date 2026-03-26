# Report Test

**Code for this page:**

```javascript
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Music Analyzer Report</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>

<header>
  <h1>Music Analyzer Report</h1>
</header>

<nav>
  <a class="nav-btn" href="index.html">Home</a>
  <a class="nav-btn active" href="report.html">Report</a>
  <a class="nav-btn" href="queries.html">Queries</a>
  <a class="nav-btn" href="visualization.html">Visualization</a>
</nav>

<main>
  <div id="content"></div>
</main>

<footer id="main-footer">
  Footer
</footer>

<!-- Taken from example https://marked.js.org/-->
<script src="https://cdn.jsdelivr.net/npm/marked/lib/marked.umd.js"></script>
<script>
  fetch('report.md')
    .then(response => response.text())
    .then(text => {
      document.getElementById('content').innerHTML = marked.parse(text);
    });
</script>

</body>
</html>
```