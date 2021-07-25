from bs4 import BeautifulSoup
import re


class VaccineStatus(object):
    def __init__(self, org_name: str, org_address: str, org_code: str, status: str):
        self.org_name = org_name
        self.org_address = org_address
        self.status = status
        self.org_code = org_code

    def __str__(self):
        ret = ""
        ret += "기관명: {name:s} \n".format(name=self.org_name)
        ret += "주소: {addr:s} \n".format(addr=self.org_address)
        # ret += "Organization Code: {code:s} \n".format(code=self.org_code)
        ret += "상태: {stat:s}".format(stat=self.status)
        return ret


# Receive li tag of list item
def vaccine_status_parser(dom: BeautifulSoup) -> VaccineStatus:
    org_tag = dom.find(name="span", attrs={"class":"_2ZThT"})
    org_name = org_tag.text
    address_tag = dom.find(name="span", attrs={"class":"_19kF1"})
    org_address = address_tag.text
    org_code_tag = dom.find(name="div", attrs={"class":"_2NFmy"}).find(name="a")
    org_code = re.match(f"https:\/\/m.place.naver.com\/hospital\/([0-9]+)\?entry=ple", org_code_tag.attrs["href"]).group(1)
    status = ""
    try:
        status_tag = dom.find(name="a", attrs={"class":"_46SXN"}).find(name="strong")
        status = status_tag.text
    except:
        status = "PARSING_FAILED"
    return VaccineStatus(org_name=org_name, org_address=org_address, org_code=org_code, status=status)