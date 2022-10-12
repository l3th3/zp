from time import sleep
import pyotp
from subprocess import run
from enum import Enum

from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException


# Test credentials from https://developers.securedrop.org/en/latest/setup_development.html#using-the-docker-environment

SOURCE_URL = "http://127.0.0.1:8080"
JOURNALIST_URL = "http://127.0.0.1:8081"
JOURNALIST_USERNAME = "journalist"
JOURNALIST_PASS = "correct horse battery staple profanity oil chewy"
OTP_SECRET = "JHCOGO7VCER3EJ4L"

SCAN_CMD_FMT = "zap-cli active-scan {url}"
REPORT_CMD_FMT = "zap-cli report -f {cmd_ftype} -o {filename}"

class ReportType(Enum):
    XML = 1
    HTML = 2
    MARKDOWN = 3


def get_ff_options(proxy_addr="127.0.0.1:8090") -> FirefoxOptions:
    options = FirefoxOptions()
    options.set_preference("network.proxy.allow_hijacking_localhost", True)
    options.set_preference("network.proxy.testing_localhost_is_secure_when_hijacked", True)
    proxy = Proxy()
    proxy.http_proxy = proxy_addr
    proxy.ssl_proxy = proxy_addr
    options.proxy = proxy
    options.headless = True
    return options


def start_driver() -> Firefox():
    options = get_ff_options()
    return Firefox(options=options)


def prepare_source_iface(base_url: str, driver: Firefox):
    generate_url = base_url + "/generate"
    driver.get(generate_url)
    elem = driver.find_element(By.ID, "codename")
    codename = elem.text
    continue_btn = driver.find_element(By.ID, "create-form").find_element(By.TAG_NAME, "button")
    continue_btn.click()


def prepare_journalist_iface(base_url: str, driver: Firefox):
    login_url = base_url + "/login"
    driver.get(login_url)
    username_el = driver.find_element(By.ID, "username")
    username_el.send_keys(JOURNALIST_USERNAME)
    pass_el = driver.find_element(By.ID, "login-form-password")
    pass_el.send_keys(JOURNALIST_PASS)
    otp_el = driver.find_element(By.ID, "token")
    otp = get_otp(OTP_SECRET)
    otp_el.send_keys(otp)
    login_btn = driver.find_element(By.TAG_NAME, "button")
    login_btn.click()


def get_otp(secret) -> str:
    return pyotp.TOTP(secret).now()


def export_report(outfile="zap_report.html", filetype=ReportType.HTML):
    if filetype == ReportType.HTML:
        cmd_ftype = "html"
    elif filetype == ReportType.XML:
        cmd_ftype = "xml"
    elif filetype == ReportType.MARKDOWN:
        cmd_ftype = "md"
    else: raise ValueError("filetype is not one of: ReportType.HTML, ReportType.XML, ReportType.MARKDOWN")
    cmdstr = REPORT_CMD_FMT.format(cmd_ftype=cmd_ftype, filename=outfile)
    res = run(cmdstr, shell=True, check=True)
    return res.returncode


def run_zap_scan(base_url: str, outfile="report.html") -> bool:
    cmdstr = SCAN_CMD_FMT.format(url=base_url)
    res = run(cmdstr, shell=True)
    if res.returncode != 0:
        return False
    if export_report(outfile=outfile) != 0:
        return False
    return True


def scan(base_url: str, login_fn=None, report_file="report.html"):
    driver = start_driver()
    driver.get(base_url)
    sleep(2)
    if login_fn:
        login_fn(base_url, driver)
    run_zap_scan(base_url, outfile=report_file)
    driver.quit()


def test_proxy_connection(test_url: str):
    driver = start_driver()
    for i in range(10):
        try:
            driver.get(test_url)
            break
        except WebDriverException:
            sleep(10)
    driver.quit()


def test_connection(url: str, test_fn):
    driver = start_driver()
    for i in range(10):
        try:
            driver.get(url)
            test_fn(driver)
            break
        except NoSuchElementException:
            sleep(10)
    driver.quit()


def src_check(driver: Firefox):
    driver.find_element(By.ID, "codename")


def jrn_check(driver: Firefox):
    driver.find_element(By.ID, "username")


def wait_for_services():
    test_proxy_connection(SOURCE_URL)
    test_connection(JOURNALIST_URL, jrn_check)
    test_connection(SOURCE_URL, src_check)


def main():
    jrn_res = scan(JOURNALIST_URL, login_fn=prepare_journalist_iface, report_file="jrn_report.html")
    src_res = scan(SOURCE_URL, login_fn=prepare_source_iface, report_file="src_report.html")
    if not src_res or not jrn_res:
        exit(1)


if __name__ == "__main__":
    main()