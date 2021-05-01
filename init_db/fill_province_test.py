from init_db.fill_province import get_province_by_gaode

if __name__ == '__main__':
    result = get_province_by_gaode("北京")
    print(result)