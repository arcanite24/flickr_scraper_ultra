<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flickr Photo Fetcher</title>
</head>
<body>
<h1>Flickr Photo Fetcher</h1>
<p>This script fetches photos from Flickr based on specified tags and saves the photo information and images to a local directory.</p>
<h2>Features</h2>
<ul>
<li>Fetch photos from Flickr using specified tags.</li>
<li>Save photo information in JSON format.</li>
<li>Download and save images in the specified format and size.</li>
<li>Parallel processing for faster downloads.</li>
</ul>
<h2>Requirements</h2>
<ul>
<li>Python 3.x</li>
<li>Required Python packages (listed in <code>requirements.txt</code>):
<ul>
<li><code>requests</code></li>
<li><code>tqdm</code></li>
</ul>
</li>
</ul>
<h2>Installation</h2>
<ol>
<li>Clone the repository:
<pre><code>git clone https://github.com/yourusername/flickr-photo-fetcher.git
cd flickr-photo-fetcher</code></pre>
</li>
<li>Install the required packages:
<pre><code>pip install -r requirements.txt</code></pre>
</li>
<li>Obtain a Flickr API key and save it in a file named <code>FLICKR_API_KEY</code> in the root directory of the project.</li>
</ol>
<h2>Usage</h2>
<p>Run the script with the following command:</p>
<pre><code>python main.py &lt;tags&gt; [--output OUTPUT] [--cores CORES] [--per_page PER_PAGE] [--sort SORT] [--max_pages MAX_PAGES] [--size SIZE] [--format FORMAT]</code></pre>
<h3>Arguments</h3>
<ul>
<li><code>tags</code> (required): Tags to search for photos.</li>
<li><code>--output</code> (optional): Output folder for saving photo information (default: <code>output</code>).</li>
<li><code>--cores</code> (optional): Number of cores to use for parallel processing (default: <code>16</code>).</li>
<li><code>--per_page</code> (optional): Number of photos per page (min 5, max 500, default: <code>500</code>).</li>
<li><code>--sort</code> (optional): Sort order of the photos (default: <code>relevance</code>).</li>
<li><code>--max_pages</code> (optional): Maximum number of pages to fetch (default: <code>10</code>).</li>
<li><code>--size</code> (optional): Size suffix for the images (e.g., <code>s</code>, <code>q</code>, <code>t</code>, <code>m</code>, <code>n</code>, <code>w</code>, <code>z</code>, <code>c</code>, <code>b</code>, <code>h</code>, <code>k</code>, <code>3k</code>, <code>4k</code>, <code>f</code>, <code>5k</code>, <code>6k</code>, <code>o</code>, default: <code>b</code>).</li>
<li><code>--format</code> (optional): Format of the images (e.g., <code>jpg</code>, <code>png</code>, default: <code>png</code>).</li>
</ul>
<h3>Example</h3>
<pre><code>python main.py "nature,landscape" --output my_photos --cores 8 --per_page 100 --sort interestingness-desc --max_pages 5 --size m --format jpg</code></pre>
<p>This command will fetch photos tagged with "nature" and "landscape", save the information and images in the <code>my_photos</code> directory, use 8 cores for parallel processing, fetch 100 photos per page, sort by interestingness in descending order, fetch up to 5 pages, and save images in medium size and JPG format.</p>
<h2>License</h2>
<p>This project is licensed under the MIT License.</p>
</body>
</html>