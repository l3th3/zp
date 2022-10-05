from time import sleep

from selenium import webdriver
from selenium.webdriver import FirefoxOptions


def get_ff_options(proxy_addr="127.0.0.1:8090") -> FirefoxOptions:
    options = FirefoxOptions()
    options.set_preference("network.proxy.allow_hijacking_localhost", True)
    options.set_preference("network.proxy.testing_localhost_is_secure_when_hijacked", True)
    proxy = webdriver.common.proxy.Proxy()
    proxy.http_proxy = proxy_addr
    proxy.ssl_proxy = proxy_addr
    options.proxy = proxy
    # options.headless = True
    return options


def run_zap_scan(addr):
    options = get_ff_options()
    driver = webdriver.Firefox(options=options)
    driver.get(addr)
    sleep(10)
    # driver.quit()


def main():
    run_zap_scan("http://127.0.0.1:8080")


if __name__ == "__main__":
    main()