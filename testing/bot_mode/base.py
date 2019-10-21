import csv
import os
import discord

from discord.ext import commands

class Base:
    #def __init__(self, bot):
    #   self.data = None

    #Method used to convert a large list into a neat string with the given constraints, converting
    #each member of the list from data to data.name for the purpose of the discord bot.
    async def convert_long_list(list, max_individual_length, max_total_length, end_data=None):

    #'end_data' is the piece of data which is skipped to when the string becomes greater than
    #or equal to max_total_length and the rest of the list is ignored.
    #Example: list[:max_total_length] + '...' + end_data
    #If this limit is not reached, 'end_data' is not used.
    
        if end_data is None: #If the end_data is undefined, set it to the final item in the list
            if len(list) > 1: #Don't want this data to be displayed twice
                end_data = list[len(list)-1]

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
                output += f' ... {end_data[:max_individual_length]}'
                if len(end_data) > max_individual_length:
					output += '(...)'
                break

        return output

    async def csv_input_prune(filename): #Removes repeated inputs
        #os.chdir('../bot_mode') --- Unnecessary as we are already in this directory.
        with open(filename, 'r') as csvdata:
            reader = csv.reader(csvdata)

            input_list = []
            rows = []

            for row in reader:

                if row != []:
                    input_duplicate = False

                    if row[0] in input_list: #Check every input in the column for duplicates
                        original_index = input_list.index(row[0])
                        input_duplicate = True
                    input_list.append(row[0])

                    if input_duplicate == False:
                        rows.append(row)

                    else:
                        merged_row = rows[original_index]
                        print(len(input_list))
                        print(len(rows))
                        rows.pop(original_index) #Remove the original
                        input_list.pop(original_index) #Remove the input to line up with 'rows'
                        for x in range(1,len(row)): #Skip the input
                            merged_row.append(row[x]) #Append any responses that can be found
                            print(merged_row)
                        print(rows[len(rows)-1])
                        #rows.pop(rows.index(row)) #Remove the new row that was added; this is replaced with the merged row on the line below

                        rows.append(merged_row)

        with open(filename, 'w') as csvwrite:
            writer = csv.writer(csvwrite)

            for row in rows:
                writer.writerow(row)

    async def csv_output_prune(filename): #Removes repeated outputs
        with open(filename, 'r') as csvdata:
            reader = csv.reader(csvdata)

            rows = []
            row_items = []

            for row in reader:
                row_items.clear()

                for x in range(0,len(row)): #Check every item in the row for duplicates (even the input as this may cause infinite loops)
                    if row[x] in row_items:
                        row_items.pop(row_items.index(row[x]))
                    row_items.append(row[x])
                    #print('row items')
                    #print(row_items)

                row.clear()
                for x in range(0, len(row_items)):
                    row.append(row_items[x])
                #print('row')
                #print(row)

                if row != []:
                    rows.append(row)
                    #print('rows')
                    #print(rows)

        with open(filename, 'w') as csvwrite:
            writer = csv.writer(csvwrite)

            for row in rows:
                writer.writerow(row)

    async def check_for_blanks(filename):
        with open(filename, 'r') as csvdata:
            reader = csv.reader(csvdata)

            rows = []
            row_items = []

            for row in reader:
                row_items.clear()

                #for x in range(0,len(row)): #Check every item in the row for duplicates (even the input as this may cause infinite loops)
                #    if row[x] == '':
            #            rows.pop(row)
            #        rows.append(row)
                    #print('row items')
                    #print(row_items)

            #    row.clear()
            #    for x in range(0, len(row_items)):
            #        row.append(row_items[x])
                #print('row')
                #print(row)

                if row != [] and '' not in row:
                    rows.append(row)
                    #print('rows')
                    #print(rows)

        with open(filename, 'w') as csvwrite:
            writer = csv.writer(csvwrite)

            for row in rows:
                writer.writerow(row)
