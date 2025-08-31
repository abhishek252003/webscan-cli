Webscan-cli isn't just another directory scanner. It's a lightweight, powerful, and elegant tool designed to run entirely in your terminal. It helps security professionals and developers find hidden directories, files, and endpoints on a web server with unmatched speed and clarity.

✨ Why Webscan-cli?
🚀 Built for Speed: Leverages multi-threading to perform scans at high velocity. Don't wait, discover.

🎨 Visual Clarity: Real-time, color-coded output tells you what's important at a glance.

📊 Organized Intelligence: The final summary isn't just a list—it's a clean, side-by-side columnar report that makes analysis effortless.

🔧 Total Control: Runs entirely from the command line. Easily scriptable and perfect for any environment, from your local machine to a remote server.

🛠️ Get Started
Getting up and running is simple. The tool is designed for Linux-based systems like Kali.

1. Installation
First, clone the repository and install the dependencies.

Bash

# Clone this repository
git clone https://github.com/abhishek252003/webscan-cli.git
cd webscan-cli

# Install the single required Python library
pip3 install -r requirements.txt
2. Make it Executable
Give the script execution permissions to run it like a native command.

chmod +x webscan-cli

🕹️ How to Use
The syntax is designed to be simple and intuitive.

Quick Start
Provide a target URL and a wordlist—that's all it takes.


python ./webscan -u <TARGET_URL> -w <WORDLIST_PATH>

Full Power Example
Scan a target using a professional wordlist from Kali's SecLists with 50 threads.

Bash

python ./webscan-cli -u http://example.com -w <WORDLIST_PATH > -t 50
Command-Line Arguments
Flag	Description	Example
-u, --url	(Required) The target URL to scan.	http://example.com
-w, --wordlist	(Required) Path to the wordlist file.	wordlist.txt
-t, --threads	Number of threads to use (default: 10).	-t 50
-a, --user-agent	Set a custom User-Agent (default: Mozilla/5.0).	-a "MyScanner/1.0"


⚠️ Disclaimer
This tool is intended for educational purposes and for use in authorized security testing scenarios only. Using this tool against systems you do not have explicit permission to test is illegal. The author is not responsible for any misuse or damage caused by this program. Always act ethically and responsibly.
