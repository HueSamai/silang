import sys


class ErrorPacket:
    def set_error_fields(self, line, char_index, file):
        self.line = line
        self.char_index = char_index
        self.file = file
        return self


class VarException(Exception):
    pass


class Error:
    stage = "Command"
    error_occurred = False

    raw_lines = {}

    padding = 20

    @staticmethod
    def report(message, line, char_index, file):
        Error.error_occurred = True

        raw_line = Error.raw_lines[file][line - 1]

        left_padding = min(Error.padding, char_index)

        right = char_index + Error.padding * 2 - left_padding
        surrounding_characters = raw_line[max(0, char_index - Error.padding):min(len(raw_line), right)]

        left = " " * 7

        if char_index <= Error.padding:
            left += "   "
        else:
            left += "..."

        print(f"{Error.stage}Error in {file}[at line {line}:{char_index}]: {message}\n" +
              left + surrounding_characters + ("...\n" if right < len(raw_line) else "\n")
              + " " * (10 + left_padding) + "^", file=sys.stderr)

        print("\n")

    @staticmethod
    def report_packet(message, packet: ErrorPacket):
        Error.report(message, packet.line, packet.char_index, packet.file)

    @staticmethod
    def report_flat(message):
        print(f"{Error.stage}Error: {message}", file=sys.stderr)
