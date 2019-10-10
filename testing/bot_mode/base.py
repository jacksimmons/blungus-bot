class Base:
    #def __init__(self, bot):
    #   self.data = None

    #Method used to convert a large list into a neat string with the given constraints, converting
    #each member of the list from data to data.name for the purpose of the discord bot.
    def convert_long_list(list, max_individual_length, max_total_length, end_data):

    #'end_data' is the piece of data which is skipped to when the string becomes greater than
    #or equal to max_total_length and the rest of the list is ignored.
    #Example: list[:max_total_length] + '...' + end_data
    #If this limit is not reached, 'end_data' is not used.

        output = ''

        for x in range(0, len(list)):
            if len(output) < max_total_length:
                data = list[len(list)-(x+1)].name
                if output == '':
                    output = str(data)[:max_individual_length]
                else:
                    output += f', {str(data)[:max_individual_length]}'

                if len(data) >= max_individual_length:
                    output += '...'

            elif len(output) >= max_total_length:
                output += f' ... {end_data}'
                break

        return output
