import typing as tp

class Util:
    
    @staticmethod
    def numerate_lines(code : str) -> str:
        numerated_code = ""
        for i,line in enumerate(code.splitlines()) :
            numerated_code += line + f"  ##{i + 1}" + "\n"
        return numerated_code
    
    @staticmethod
    def parse_response(input : str) -> tp.List[tp.Dict] : 
        print("Full response:")
        if input is None or not input:
            return []
        
        lines = input.strip().split("\n")
        response = []

        for full_text in lines:
            print(full_text)
            number_str = ''
            number = 0
            full_text = full_text.strip()
            if len( full_text ) == 0:
                continue

            reading_number = True
            for char in full_text.strip():
                if reading_number:
                    if char.isdigit():
                        number_str += char
                    else:
                        break

            if number_str:
                number = int(number_str)

            response.append({"line" : number, "comment" : full_text})
        return response
    
    @staticmethod
    def parse_diffs(diff : str) -> tp.List[tuple[int,int]]:
        intervals : tp.List[tuple[int,int]] = []
        for line in diff.splitlines():
            if line.startswith("@@"):
                try:
                    start,context = line[line.find('+') + 1 : -2].split(',')
                    context = context.split("@@")[0]
                    end = int(start) + int(context) - 1
                    intervals.append((int(start),end))
                except:
                    continue
        
        return intervals
    
    @staticmethod
    def check_availability_to_post_comment(line_number : int, intervals : tp.List[tuple]) -> bool:
        for start, end in intervals:
            if start <= line_number <= end:
                return True
        return False