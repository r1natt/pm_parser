import json
from reqs import get_page
from pprint import pprint


def unparse():
    with open("response.json") as f:
        data = json.load(f)

    # pprint(data["CNT"][0]["CL"][0]["E"])
    # pprint(len(data["CNT"][0]["CL"][0]["E"][0]["StakeTypes"]))

    for match in data["CNT"][0]["CL"][0]["E"]:
        print(match["CId"], end=" ")  # id лиги
        print(match["H2HId"], end=" ")  # айди матча (скорее всего)
        print(match["HT"], end=" - ")  # первая команда
        print(match["AT"], end=" ")  # вторая команда
        print(match["D"], end=" ")  # дата и время матча
        for strake_type in match["StakeTypes"]:
            if strake_type["Id"] == 3:
                stakes = strake_type["Stakes"]
                print(stakes[0]["A"], end=" ")  # тотал 
                print(stakes[0]["N"], end=" ")  # больше или меньше
                print(stakes[0]["F"])  # коэф

                break

unparse()


if __name__ == "__main__":
    pass
