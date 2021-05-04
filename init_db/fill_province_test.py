from init_db.fill_province import get_province_by_gaode, get_location_by_gaode

if __name__ == '__main__':
    # result = get_province_by_gaode("北京")
    # print(result)
    result = get_location_by_gaode("扬州")
    print(result)