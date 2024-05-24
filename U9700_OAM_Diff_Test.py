
import U9700_PIU_16S_Redstone_OAM_Converter as RedStone
import U9700_PIU_16SC_Aspen_OAM_Converter as Aspen
from datetime import datetime



###############################################################################################################
#       HexaOneLine로 변환된 DumpList를 넣으면 자기 중에 중복 요소를 Check하고 삭제한다.
###############################################################################################################
def RemoveDuplicationInDumpHexaList(DumpHexList : list):
    DupliCount = 0

    for Compare1 in list(DumpHexList):  # Create a copy of the list for iteration
        if DumpHexList.count(Compare1) > 1:  # If the element appears more than once
            DumpHexList.remove(Compare1)  # Remove it from the original list
            DupliCount += 1

    return DupliCount



###############################################################################################################
#       HexaOneLine로 변환된 DumpList의 요소를 집어넣으면 아래의 Dict 형태로 변환한다. - 아래 함수에서 사용
###############################################################################################################
def ParseDatatoDict(data):
    # 각 구조로 분리하여 딕셔너리로 저장
    parsed_data = {

        "Dst" : data [:6 * 2],                  # 6 Byte
        "Src" : data [6 * 2 : 12 * 2],          # 6 Byte
        "Len_Type" : data [12 * 2 : 14 * 2],    # 2 Byte
        "Subtype": data[14 * 2: 15 * 2],        # 1 Byte
        "Flags": data[15 * 2: 17 * 2],          # 2 Byte
        "Code": data[17 * 2: 18 * 2],           # 1 Byte
        "DataAndPad": data[18 * 2: ],           # Rest

        "FullData": data,                       # Hexa 형식 전체도 저장한다.
    }

    return parsed_data




###############################################################################################################
#       HexaOneLine로 변환된 DumpList를 OAM Header 부분대로 나누어서 Dict에 저장한 것을 List로 반환한다.
###############################################################################################################
def MakeListParsedDict(DumpHexaList : list):
    RetList = []

    for Data in DumpHexaList:
        DictData = ParseDatatoDict(Data)
        RetList.append(DictData)

    return RetList




###############################################################################################################
#       DumpHexaDictList를 통해서 OAM Header가 0x0050 값이 아닌 것을 선별하여 return한다.
###############################################################################################################
def CheckOAM_HeaderFlag_0x0050(DumpHexaDictList: list):
    Not0x0050FlagList = []

    for OAM in DumpHexaDictList:
        if OAM["Flags"] == "0050":
            Not0x0050FlagList.append(OAM)

    return Not0x0050FlagList






###############################################################################################################
#       Diff Test에 필요한 Branch 값에 대한 문자 데이터를 준비한다.
###############################################################################################################

'''
[ 설명 : BranchNameDict ]

    Key = Hexa, String [브랜치 값]      ex) 07, 09, A7
    Value = String [브랜치 이름]         ex) Attributes, Actions, KT Attributes         

- 사용 목적 : Hexa String 값으로 맞는 Branch Name을 얻기 위해서 선언
'''
BranchNameDict = {}


'''
[ 설명 : BranchLeafStringDict ]

    Key = Hexa, String [브랜치 값]      ex) 07, 09, A7
    Value = {} : Dict
        Key =  Hexa, String [leaf 값]    ex) 00BF, 001A, 003D...
        Value = list
            Branch 07 : 1. leafname : str   , 2. R/W : std  , 3. Description : str 
            Branch 08 : 1. leafname : str   , 2. Description : str
        
- 사용 목적 : 브랜치 값별로 Leaf에 대한 정보를 정리하고 해당 leaf에 대하여 leafNameString, Description을 정리하기 위해 선언
'''
BranchLeafStringDict = {}


# 만약 Branch 파일에 대한 값이 추가된다면 이 함수를 수정해야 한다.
# 입력 값 : Branch에 해당하는 Byte Value
def SetBranchLeafStringData(BranchByte_HEXA: str):

    # 1. 내용 추가 시 아래 내용 추가. ####################################
    if BranchByte_HEXA == "07":
        FileName = "U9700/Branch07"
        AttributeName = "Attributes"

    elif BranchByte_HEXA == "09":
        FileName = "U9700/Branch09"
        AttributeName = "Actions"
    ##################################################################

    BranchNameDict[BranchByte_HEXA] = AttributeName
    BranchLeafStringDict[BranchByte_HEXA] = {}  # Dict 생성 - 위의 내용처럼 key = leafvalue, value = list [1. leafName, ... Description ]

    BranchInfoFile = open(FileName, 'r', encoding="UTF-8")

    while True:
        line = BranchInfoFile.readline()

        # 파일의 마지막이라면 작업 종료
        if not line:
            break

        # 라인의 시작이 *, /, "\n" 이라면 넘어간다.
        if line.startswith("*") or line.startswith("/"):
            continue
        if line == "\n":
            continue

        # 2. 내용 추가 시 아래 내용 추가 ##########################################################################################################
        if BranchByte_HEXA == "07":
            LeafAndDescript = line.split(",", 3)    # 파일 문장을 ,을 구분자로 세팅해놨다.
            Name = str(int(LeafAndDescript[0].replace(" ", ""), 16))    # leafValue 동일하다.
            BranchLeafStringDict[BranchByte_HEXA][Name] = []    # leafValue를 Key로 list를 Value로 삽입한다.

            # 1. leafName
            BranchLeafStringDict[BranchByte_HEXA][Name].append(LeafAndDescript[1])
            # 2. R/W
            BranchLeafStringDict[BranchByte_HEXA][Name].append(LeafAndDescript[2])
            # 3. Description
            BranchLeafStringDict[BranchByte_HEXA][Name].append(LeafAndDescript[3].replace("\n", ""))


        elif BranchByte_HEXA == "09":
            LeafAndDescript = line.split(",", 2)    # 위와 동일
            Name = str(int(LeafAndDescript[0].replace(" ", ""), 16))
            BranchLeafStringDict[BranchByte_HEXA][Name] = []

            # 1. leafName
            BranchLeafStringDict[BranchByte_HEXA][Name].append(LeafAndDescript[1])
            # 2. Description
            BranchLeafStringDict[BranchByte_HEXA][Name].append(LeafAndDescript[2].replace("\n", ""))

        ####################################################################################################################################

    BranchInfoFile.close()




###############################################################################################################
#       OAM Width에 대하여 값이 128 초과라면 Log를 남기기 위해서 Width와 관련된 Information을 초기화하는 함수
###############################################################################################################
'''
 [ 설명 : WithErrorDict ]
 
    key = Hex, String [Width Value]     ex) 80, 81, A1, A2
    value =  list [ 1. ErrorName, 2. ErrorDescription ]

- 사용 목적 : OAM에 있어 128보다 넘어가는 width는 0 parameter 이며, 이중 128을 제외한 몇 개의 값은 Error Code이다. 
    이러한 information을 통해 출력 데이터에 추가하기 위해서 선언.
'''
WithErrorDict = {}

# 추가적인 내용은 없을 것 같으며 이대로 사용하면 된다.
def SetOAM_WidthErrorInformation():

    WidthErrorInfoFile = open("U9700/OAM_WidthError", "r", encoding="UTF-8")

    while True:
        line = WidthErrorInfoFile.readline()

        if not line:
            break
        if line == "\n":
            continue

        SplitString = line.split(",")

        Key = SplitString[2].replace(" ", "").replace("\n", "")

        WithErrorDict[Key] = []
        WithErrorDict[Key].append(SplitString[0])
        WithErrorDict[Key].append(SplitString[1])

    WidthErrorInfoFile.close()


###############################################################################################################
#       OAM MSG에 있는 요소로서 각 Op HEX 값 당 다음과 같은 이름 정보를 가지고 있다.
###############################################################################################################

OpName = {
    "00": "[00]Info",
    "01": "[01]Get Request",
    "02": "[02]Get Response",
    "03": "[03]Set Request",
    "04": "[04]Set Response",
}


###############################################################################################################
#       Width가 이상 값에 대해서 출력을 하려는 함수
###############################################################################################################

def PrintLogWidthError(OutPutFileName: str, WidthErrorDict: dict, ResetFileFlag: bool = False):

    if ResetFileFlag:
        OutPutFile = open(OutPutFileName, "w")
    else :
        OutPutFile = open(OutPutFileName, "a+")


    OutPutFile.write("////////////////////////////////////////////////////////////////////////////////\n")
    OutPutFile.write("//\t\t Width Error Msg\n")
    OutPutFile.write("////////////////////////////////////////////////////////////////////////////////\n")



    # 해당 Log를 보는데 있어 주의해야할 점을 기재. ####################################################
    OutPutFile.write("\nNote: \n")
    OutPutFile.write(
        "\t1. 작업 기준(wiki) : https://wiki.ubiquoss.com/download/attachments/110930728/EPON_ONUxG-PG302-R26X-R33X-RDS%20-%20BRCM%20OAM%20Extension.pdf?api=v2\n\t\t3.2.4 Broadcom(Tek) OAM message.pdf - page.28\n")
    OutPutFile.write(
        "\t2. Branch:0x07, Leaf:0x00B9(249)에 대한 내용이 PDF에 없습니다. 이와같은 데이터는 LeafName과 Description이 - 로 표시됩니다.\n")
    OutPutFile.write("\t3. ~~~~ 확인 필요 ~~~~ 값은 나오면 안됩니다.\n")


    '''
     [ 설명 : WidthErrorDict ]
     
        key = String [PonChipName]      ex) Redstone, Aspen(EMGRD)
        Value = {}
            Key = Hex, String [Width]   ex) 80, 81, A1, A2
            Value = list [1. Op Hex : str   , 2. Branch Hex : str   , 3. leaf Hex :str  , 4. FullOamData :str ]
    
    - 사용 목적 : Width에 따른 Error String을 출력하기 위해서 만든 Dictionary이다.
    '''

    for PonChipName, PonDict in WidthErrorDict.items():

        # 폰 칩에 대한 이름을 적기 위한 코드
        InputString = "\n"
        InputString += "----------------------------------------------------\n"
        InputString += ("| PonChipName: " + PonChipName + "\n")
        InputString += "----------------------------------------------------\n\n"

        for Width, OpBranchLeafFull_List in PonDict.items():

            # Width의 키가 WithErrorDict- info에 저장되어 있지 않다면, 일단 작업을 하지 않는다. <- 나중에 수정.
            if not Width in WithErrorDict:
                InputString += ("\n ????? Width : " + Width + " // FullOam : " + List[3] + "\n\n");
                continue
            InputString += ("Error Width = 0x" + Width + " : " + WithErrorDict[Width][0] + " -" + WithErrorDict[Width][
                1] + "\n\n")

            for List in OpBranchLeafFull_List:
                InputString += ("\t OP :" + " [" + OpName[List[0]] + "]")

    OutPutFile.close()



###############################################################################################################
#       Extract Value From OAM MSG
###############################################################################################################



def ExtractFromOAM(OamDataList : dict, StoreDict : dict, PonChipName: str):

    CheckList = []
    ErrorAttributeWithWidth = {}

    for OamData in OamDataList:


        OamDataAndPad = OamData.get("DataAndPad")

        # 이것을 기준으로 Var에 대한 값을 가져갈 것이다.
        StrLen = len(OamDataAndPad)

        # 3Byte = OUI, 1Byte = Op
        if StrLen < 4 * 2:
            return -1

        # OUI 3 Byte
        OUI = OamDataAndPad[ 0 : 3*2 ]
        #print("OUI = " + OUI)

        # 1 Byte
        #해당 op 값을 기반으로 아래의 값이 매칭이 될 듯 하다. + OUI 에 대해서도 변경
        Op = OamDataAndPad[ 3*2 : 4*2]
        #print("Op =  " + Op)

        # 현재 Op 코드가 0 (info), 1 () 인것은 제외하였다. - 이유 : Branch-Leaf-Width-Value에 대한 정보가 나오지 않는다.
        if (int(Op, 16) != 2) and (int(Op, 16) != 3) and (int(Op, 16) != 4):
            return -1





        ########################################################
        # 여기부터 Var영역이다. - 반복문으로 전환해야 한다.            #
        ########################################################
        '''
        # Branch 1바이트이다. - HEX 값인것을 인지 해야 한다.
        Branch = OamDataAndPad[ 4*2 : 5*2 ]
    
        # 이것도 고려를 해야 한다.
        if Branch == "07":
            print("0x07 is Attribute!!")
    
        # 위의 Branch가 07이면, 아래 2 Byte가 leaf이다.   // leaf가 아닌 경우도 있지만, 2바이트를 차지하는 것은 같다.
        leaf = OamDataAndPad[ 5*2 : 7*2 ]
        print("leaf : " + leaf)
    
        # 위가 1바이트 leaf라면은 여기는 Width 값이다.    // leaf가 아닌 경우에도 지금 length 값으로 width와 비슷한 역할을 한다.
        width = OamDataAndPad[ 7*2 : 8*2 ]
        print("width : " + width)
    
        # 현재는 일단 ... 이대로 놔두자.
        ParsedData = OamDataAndPad[ 8*2 : (8 + width)*2 ]
        '''


        WorkByte = 4

        while(True):
            if StrLen <= WorkByte*2:
                break

            LeafFlag = True

            # Branch 1바이트이다. - HEX 값인것을 인지 해야 한다.
            Branch = OamDataAndPad[WorkByte * 2: (WorkByte+1) * 2]
            #print(Branch)
            WorkByte += 1



            # 아외에 추가적인 사항이 있다면은 기재를 해야한다.
            if Branch == "00":
                print("0x00 is End!!")
                break

            if Branch == "06":
                LeafFlag = False
                print("Not Leaf Data... ")


            # 위의 Branch가 07이면, 아래 2 Byte가 leaf이다.   // leaf가 아닌 경우도 있지만, 2바이트를 차지하는 것은 같다.
            leaf = OamDataAndPad[WorkByte * 2: (WorkByte+2) * 2]
            WorkByte += 2


            # 위가 1바이트 leaf라면은 여기는 Width 값이다.    // leaf가 아닌 경우에도 지금 length 값으로 width와 비슷한 역할을 한다.
            width = OamDataAndPad[WorkByte * 2: (WorkByte+1) * 2]
            WorkByte += 1


            if int(width, 16) >= 128:

                if int(width, 16) > 128:
                    if not PonChipName in ErrorAttributeWithWidth:
                        ErrorAttributeWithWidth[PonChipName] = {}
                    if not width in ErrorAttributeWithWidth[PonChipName]:
                        ErrorAttributeWithWidth[PonChipName][width] = []

                    PushList = []
                    PushList.append(Op)
                    PushList.append(Branch)
                    PushList.append(leaf)
                    PushList.append(OamData["FullData"])

                    ErrorAttributeWithWidth[PonChipName][width].append(PushList)
                    '''
                    if int(leaf,16) == 249 :
                        print(OamData["FullData"])
                        input()
                    '''
                    '''
                    if width == "9F":
                        print(OamData["FullData"])
                        input()
                    '''


                width = "00"
                LeafFlag = False


            # 현재는 일단 ... 이대로 놔두자.
            ParsedData = OamDataAndPad[WorkByte * 2: (WorkByte + int(width, 16)) * 2]
            OldWorkByte = WorkByte
            WorkByte += int(width, 16)

            if LeafFlag:
                #print("leaf : 0x" + leaf + " width : 0x" + width + " Data : " + ParsedData)
                #print()
                # StoreDict[int(leaf, 16)] = int(Branch, 16)

                # 나중에 빼야 하는 코드 - 이상값을 찾기 위한 코드

                '''
                #if int(Branch, 16) == 167:# and int(leaf, 16) == 184 :
                    #print("Op :" + str(int(Op, 16)) + " leaf : " + str(int(leaf, 16)) + " Width : " + str(int(width, 16)))
                    #print(OamData["FullData"]);
                    #input()
                '''


                # key = str(int(Branch, 16)) + "-" + str(int(leaf, 16))
                key = str(int(Branch, 16)) + "-" + str(int(leaf, 16)) + " " + Op

                if not key in CheckList:
                    StoreDict[key] = set()
                    CheckList.append(key)

                if StrLen < WorkByte*2:
                    ParsedData = "*" + ParsedData
                    #print("strlen: " + str(StrLen) + " WorkByte : " + str(WorkByte*2) + " OldWorkByte: " + str(OldWorkByte*2) + " width : " + width)
                    #print(OamData["FullData"]);
                    #input()
                else :
                    ParsedData = " " + ParsedData

                #ParsedData += "/" + OamData["FullData"]
                #StoreDict[key].append(ParsedData);
                StoreDict[key].add(ParsedData)

    return ErrorAttributeWithWidth








###############################################################################################################
#       Extract Value From OAM MSG
###############################################################################################################
def CompareTwoDictData(Comp1: dict, Comp2: dict,
                       MakeFileName: str, Comp1Name: str, Comp2Name: str,
                       PrintSameValueFlag: bool,
                       ResetFlag: bool):
    DiffDicts = {
        "00": [],
        "01": [],
        "02": [],
        "03": [],
        "04": [],
    }
    SameDicts = {
        "00": [],
        "01": [],
        "02": [],
        "03": [],
        "04": [],
    }

    if ResetFlag:
        MakeFile = open(MakeFileName, 'w', encoding='UTF-8')
    else:
        MakeFile = open(MakeFileName, 'a+', encoding='UTF-8')

    DiffCount = 0
    SameCount = 0

    for TargetKey, TargetList in Comp1.items():

        for Data in TargetList:
            # Comp의 Value를 순횐한다.
            if TargetKey in Comp2:

                for CompValue in Comp2[TargetKey]:

                    inName = TargetKey.split(" ")
                    InputString = ""

                    InputString += ("[Branch-Leaf]:".center(17) + " " + inName[0])
                    BranchLeaf = inName[0].split("-")

                    if BranchLeaf[0] in BranchLeafStringDict:
                        FindDict = BranchLeafStringDict[BranchLeaf[0]]

                        if BranchLeaf[0] == "7":
                            print(BranchLeaf[1])
                            print(type(BranchLeaf[1]))

                            LeafName = FindDict[BranchLeaf[1]][0]
                            ReadOrWrite = FindDict[BranchLeaf[1]][1]
                            Description = FindDict[BranchLeaf[1]][2]
                            InputString += (" [Branch :" + BranchNameDict[BranchLeaf[0]] + ", ")
                            InputString += (
                                        "LeafName :" + LeafName + ", R/W :" + ReadOrWrite + "] - Description :" + Description)

                        elif BranchLeaf[0] == "9":
                            LeafName = FindDict[BranchLeaf[1]][0]
                            Description = FindDict[BranchLeaf[1]][1]
                            InputString += (" [Branch :" + BranchNameDict[BranchLeaf[0]] + ", ")
                            InputString += ("LeafName :" + LeafName + "] - Description :" + Description)

                    else:
                        if BranchLeaf[0] == "167":
                            InputString += " [데이터 부재]"
                        else:
                            InputString += " [~~~확인 필요~~~~]"

                    InputString += "\n"
                    InputString += ("[" + Comp1Name.center(15) + "]: " + Data + "\n")
                    InputString += ("[" + Comp2Name.center(15) + "]: " + CompValue + "\n\n")

                    if Data != CompValue:
                        DiffCount += 1
                        DiffDicts[inName[1]].append(InputString)
                    else:  # Data == CompValue
                        SameCount += 1
                        SameDicts[inName[1]].append(InputString)

    # 현재 날짜와 시간을 가져옵니다.
    now = datetime.now()
    # 날짜와 시간을 문자열로 변환합니다.
    date_string = now.strftime("%Y-%m-%d %H:%M:%S")

    MakeFile.write("////////////////////////////////////////////////////////////////////////////////\n")
    MakeFile.write("//\t\t Test : [" + Comp1Name + "] and [" + Comp2Name + "]\n")
    MakeFile.write("//\t\t Test Time : " + date_string + "\n")
    MakeFile.write("////////////////////////////////////////////////////////////////////////////////\n")

    MakeFile.write("Note: \n")
    MakeFile.write("\t1. (*) 표시는 Msg 규격보다 더 넘어가는 width에 대하여 표시했습니다. + [7-184 : Egress Shaping]에 대한 확인 필요.\n")
    MakeFile.write("\t2. Branch가 [6]Name Binding인 경우 leaf가 아니라 Object여서 해당 Branch는 제외했습니다.  \n")
    MakeFile.write("\t3. Op이 0인 Info메시지와 leaf에 value 값이 없는 Op [01]Get Request는 제외했습니다.\n")
    MakeFile.write("\t4. ~~~~ 확인 필요 ~~~~ 값은 나오면 안됩니다.\n")

    MakeFile.write("\n")
    MakeFile.write("################################################################\n")
    MakeFile.write("#\t\t\tTest Fail - Different Value [DiffCount:" + str(DiffCount) + "]\n")
    MakeFile.write("################################################################\n")

    for key, value in DiffDicts.items():
        if key == "00" or key == "01":
            MakeFile.write("[제외 : Note 참고]")
        MakeFile.write("----- " + OpName[key] + " ------\n\n")
        for InputString in value:
            MakeFile.write(InputString)
            MakeFile.flush()

    if PrintSameValueFlag:
        MakeFile.write("################################################################\n")
        MakeFile.write("#\t\t\tTest Ok - Same Value [SameCount:" + str(SameCount) + "]\n")
        MakeFile.write("################################################################\n")
        for key, value in SameDicts.items():
            if key == "00" or key == "01":
                MakeFile.write("[제외]")
            MakeFile.write("----- Op Code : " + OpName[key] + " ------\n\n")
            for InputString in value:
                print(InputString)
                MakeFile.write(InputString)
                MakeFile.flush()

    MakeFile.write("////////////////////////////////////////////////////////////////////////////////\n\n\n\n")
    MakeFile.close()