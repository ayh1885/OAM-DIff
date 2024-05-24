

TempRedStoneHexFileName = "U9700/U9700_TEMP_RedStone_OAM_HEX_DUMP.txt"

def DumpToHexData_PIU_16SC_1G(FileName:str):

    DumpFile = open(FileName, 'r')
    MakeFile = open(TempRedStoneHexFileName, 'w')

    Num = 1

    while True:

        line = DumpFile.readline()
        if not line:
            break
        # line.strip()

        PutStr = ""

        if line.startswith("D: "):
            MakeFile.write("--- N0." + str(Num) + " -------------------------------------------------\n\n")
            Num += 1

            try:
                PutStr = line.split(" ")[1] + " " + line.split(" ")[3] + " " + line.split(" ")[5].replace("[", "").replace(
                "]", "")
            except Exception as e:
                print("Abnormal Data in Dump!!!")
                print(line)
                continue

        elif line.startswith("SubType: "):
            PutStr = line.split(" ")[1] + " " + line.split(" ")[3] + "\n"

        elif line.startswith("Type"):
            try:
                PutStr = line.split(" ")[1].replace(",", "") + " " + line.split(" ")[3]
            except Exception as e:
                print("Abnormal Data in Dump!!!")
                print(line)
                continue

            else:
                line = DumpFile.readline()
                while line != "\n":
                    if not line:
                        break

                    if line.startswith("["):
                        break

                    PutStr += line
                    line = DumpFile.readline()

                PutStr += "\n\n"

        # print(PutStr)
        PutStr = PutStr.upper()
        MakeFile.write(PutStr)


    DumpFile.close()
    MakeFile.close()



    # 간단한 디버그 용 코드. - Hex로 변환
    MakeFile = open(TempRedStoneHexFileName, 'r')

    while True:
        Debug = MakeFile.readline()
        if not Debug:
            break

        if Debug.startswith("--- N0."):
            continue

        for Char in Debug:
            if (Char < '0' or '9' < Char) and (Char < 'A' or 'F' < Char) and Char != " " and Char != "\n" and (
                    Char < 'a' or 'f' < Char):
                raise "RedStoneConverterError!"

    MakeFile.close()