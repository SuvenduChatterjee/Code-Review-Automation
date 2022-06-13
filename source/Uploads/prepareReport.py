import xlsxwriter
import datetime
from pprint import pprint
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import LETTER
# add style
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

class Report: 
   
    # init method or constructor  
    def __init__(self, context):
        #Project name
        self.FlowName=context['title']

        #Stats
        self.stats={}
        self.stats['Flow count']= context['flows_count']
        self.stats['System properties']= context['sys_props']
        self.stats['System accounts']= context['sys_accts']
        self.stats['Error count']= context['error_count']
        self.stats['Warning count']= context['warning_count']

        #rules
        self.VIOLATION_MATRIX= context['violations']
        self.WARNING_MATRIX= context['warnings']

        #flow
        self.FlowDetails= context['flows']

        #System properties
        self.SysProp = context['sys_props']
        #System accounts
        self.SysAccount = context['sys_accts']

        #data
        self.data1 = []
        self.data2 = []
        self.data3 = []
        self.data4 = []


   
    # create_Report Method  
    def create_Report(self,isEnabled):
        if isEnabled:
            fileName = self.FlowName+ ' ' +datetime.datetime.now().strftime("%m-%d-%Y %H-%M-%S")
            extention = ['.xlsx', '.pdf']
            location= 'Reports/'+fileName
            workbook = xlsxwriter.Workbook(location+extention[0])
            #canvas = Canvas(location+extention[1], pagesize=LETTER)
            #PDF
            pdf = SimpleDocTemplate(
                location+extention[1],
                pagesize=LETTER
                #pagesize=(24*inch, 8.5*inch)
            )
            worksheet = workbook.add_worksheet("OO Code Review Report")
            cell_format = workbook.add_format({'bold': True, 'font_color': 'green', 'bg_color': '#C0C0C0', 'border': 1})
            warning_cell_format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': '#FFFF00', 'border': 1})
            error_cell_format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': '#FF0000', 'border': 1})
            worksheet.set_row(0, 20)
            worksheet.set_column(0, 4, 15)
            
            row=0
            column=0
            temp1=[]
            temp2=[]
            for name,stat in self.stats.items():
                #write operation perform
                row = 0
                worksheet.write(row, column, name, cell_format)
                temp1.append(name)
                row += 1
                worksheet.write(row, column, len(stat) if isinstance(stat,list) else stat)
                temp2.append(len(stat) if isinstance(stat,list) else stat)
                column += 1
            self.data1.append(temp1)
            self.data1.append(temp2)
            
            worksheet = workbook.add_worksheet("OO Code Review Details")
            cell_format = workbook.add_format({'bold': True, 'font_color': 'green', 'bg_color': '#C0C0C0', 'border': 1})
            worksheet.set_row(0, 20)
            worksheet.set_column(0, 5, 35)
            row= 0
            column= 0
            temp1=[]
            worksheet.write(row, column, "Step", cell_format)
            temp1.append("Step")
            column += 1
            worksheet.write(row, column, "Variable Type", cell_format)
            temp1.append("Variable Type")
            #column += 1
            #worksheet.write(row, column, "UUID", cell_format)
            column += 1
            worksheet.write(row, column, "Name",cell_format)
            temp1.append("Name")
            column += 1
            worksheet.write(row, column, "Assign From", cell_format)
            temp1.append("Assign From")
            column += 1
            worksheet.write(row, column, "Default Value", cell_format)
            temp1.append("Default Value")
            column += 1
            worksheet.write(row, column, "Remarks", cell_format)
            temp1.append("Remarks")
            self.data2.append(temp1)
            row += 1
            column= 0
            colorCode=[]
            for flow in self.FlowDetails:
                #Flow Inputs Start
                if len(flow['inputs']) >0:
                    for input in flow['inputs']:
                        if(len(input['violations']) > 0):
                            for key in input['violations']:
                                if key in self.WARNING_MATRIX:
                                    format=warning_cell_format
                                    colorCode.append(("BACKGROUND",(0,row),(5,row),'#FFFF00'))
                                else:
                                    format=error_cell_format
                                    colorCode.append(("BACKGROUND",(0,row),(5,row),'#FF0000'))
                                temp1=[]
                                worksheet.write(row, column, 'Flow Inputs',format)
                                temp1.append(self.breakLines('Flow Inputs',22))
                                column+=1
                                worksheet.write(row, column, 'Input Variable',format)
                                temp1.append(self.breakLines('Input Variable',12))
                                column+=1
                                worksheet.write(row, column, input['name'],format)
                                temp1.append(self.breakLines(input['name'],15))
                                #column+=1
                                #worksheet.write(row, column, flow['uuid'])
                                column+=1
                                worksheet.write(row, column, input['assign_from'],format)
                                temp1.append(self.breakLines(input['assign_from'],29))
                                column+=1
                                worksheet.write(row, column, input['default_value'],format)
                                temp1.append(self.breakLines(input['default_value'],40))
                                column+=1
                                worksheet.write(row, column, self.VIOLATION_MATRIX[key],format)
                                temp1.append(self.breakLines(self.VIOLATION_MATRIX[key],42))
                                self.data2.append(temp1)
                                column=0
                                row+=1
                #Flow Input ends
                #Flow Outputs Start
                if len(flow['outputs']) > 0:
                    for output in flow['outputs']:
                        if(('violations' in output.keys()) and (len(output['violations']) >0)):
                            for key in output['violations']:
                                if key in self.WARNING_MATRIX:
                                    format=warning_cell_format
                                    colorCode.append(("BACKGROUND",(0,row),(5,row),'#FFFF00'))
                                else:
                                    format=error_cell_format
                                    colorCode.append(("BACKGROUND",(0,row),(5,row),'#FF0000'))
                                temp1=[]
                                worksheet.write(row, column, 'Flow Outputs',format)
                                temp1.append(self.breakLines('Flow Outputs',22))
                                column+=1
                                worksheet.write(row, column, 'Output Variable',format)
                                temp1.append(self.breakLines('Output Variable',12))
                                column+=1
                                worksheet.write(row, column, output['name'],format)
                                temp1.append(self.breakLines(output['name'],15))
                                column+=1
                                #worksheet.write(row, column, flow['uuid'])
                                #column+=1
                                worksheet.write(row, column, output['assign_from'],format)
                                temp1.append(self.breakLines(output['assign_from'],29))
                                column+=1
                                worksheet.write(row, column, 'N/A',format)
                                temp1.append('N/A')
                                column+=1
                                worksheet.write(row, column, self.VIOLATION_MATRIX[key],format)
                                temp1.append(self.breakLines(self.VIOLATION_MATRIX[key],42))
                                self.data2.append(temp1)
                                column=0
                                row+=1
                #Flow Outputs Ends
                #Step Start
                #Step Inputs Start
                if len(flow['steps']) > 0:
                    for step in flow['steps']:
                        if step['actual_var_count'] > 0:
                            for input in step['inputs']:
                                if len(input['violations']) >0:
                                    for key in input['violations']:
                                        if key in self.WARNING_MATRIX:
                                            format=warning_cell_format
                                            colorCode.append(("BACKGROUND",(0,row),(5,row),'#FFFF00'))
                                        else:
                                            format=error_cell_format
                                            colorCode.append(("BACKGROUND",(0,row),(5,row),'#FF0000'))
                                        temp1=[]
                                        worksheet.write(row, column, step['name'], format)
                                        temp1.append(self.breakLines(step['name'],22))
                                        column+=1
                                        worksheet.write(row, column, 'Input Variable', format)
                                        temp1.append('Input Variable')
                                        column+=1
                                        worksheet.write(row, column, input['name'], format)
                                        temp1.append(self.breakLines(input['name'],15))
                                        column+=1
                                        worksheet.write(row, column, input['assign_from'],format)
                                        temp1.append(self.breakLines(input['assign_from'],29))
                                        column+=1
                                        worksheet.write(row, column, input['default_value'],format)
                                        temp1.append(self.breakLines(input['default_value'],40))
                                        column+=1
                                        worksheet.write(row, column, self.VIOLATION_MATRIX[key],format)
                                        temp1.append(self.breakLines(self.VIOLATION_MATRIX[key],42))
                                        self.data2.append(temp1)
                                        column=0
                                        row+=1
                #Step Inputs End
                #Step Ouput Starts
                            for output in step['outputs']:
                                if len(output['violations']) > 0:
                                    for key in output['violations']:
                                        if key in self.WARNING_MATRIX:
                                            format=warning_cell_format
                                            colorCode.append(("BACKGROUND",(0,row),(5,row),'#FFFF00'))
                                        else:
                                            format=error_cell_format
                                            colorCode.append(("BACKGROUND",(0,row),(5,row),'#FF0000'))
                                        temp1=[]
                                        worksheet.write(row, column, step['name'],format)
                                        temp1.append(self.breakLines(step['name'],22))
                                        column+=1
                                        if output['variable_type'] == "FLOW_OUTPUT_FIELD" :
                                            worksheet.write(row, column, 'Flow Output Variable', format)
                                            temp1.append(self.breakLines('Flow Output Variable',12))
                                        else:
                                            worksheet.write(row, column, 'Output Variable',format)
                                            temp1.append(self.breakLines('Output Variable',12))
                                        column+=1
                                        worksheet.write(row, column, output['name'],format)
                                        temp1.append(self.breakLines(output['name'],15))
                                        column+=1
                                        worksheet.write(row, column, output['assign_from'],format)
                                        temp1.append(self.breakLines(output['assign_from'],29))
                                        column+=1
                                        worksheet.write(row, column, 'N/A',format)
                                        temp1.append('N/A')
                                        column+=1
                                        worksheet.write(row, column, self.VIOLATION_MATRIX[key],format)
                                        temp1.append(self.breakLines(self.VIOLATION_MATRIX[key],42))
                                        self.data2.append(temp1)
                                        column=0
                                        row+=1
            #System Properties
            if(len(self.SysProp) > 0):
                row=0
                column=0
                temp1=[]
                worksheet = workbook.add_worksheet("OO Code Review(Sys prop)")
                cell_format = workbook.add_format({'bold': True, 'font_color': 'green', 'bg_color': '#C0C0C0', 'border': 1})
                worksheet.set_row(0, 20)
                worksheet.set_column(0, 2, 20)
                worksheet.write(row, column, 'Name',cell_format)
                temp1.append('Name')
                column+=1
                worksheet.write(row, column, 'Path',cell_format)
                temp1.append('Path')
                column+=1
                worksheet.write(row, column, 'Where it is used',cell_format)
                temp1.append('Where it is used')
                self.data3.append(temp1)
                column=0
                row+=1
                for sys_prop in self.SysProp:
                    for used_flow in sys_prop['usage']:
                        temp1=[]
                        worksheet.write(row, column, sys_prop['name'])
                        temp1.append(sys_prop['name'])
                        column+=1
                        worksheet.write(row, column, sys_prop['path'])
                        temp1.append(self.breakLines(sys_prop['path'],38))
                        column+=1
                        worksheet.write(row, column, used_flow)
                        temp1.append(used_flow)
                        self.data3.append(temp1)
                        column=0
                        row+=1
            #System Accounts
            if len(self.SysAccount) >0:
                row=0
                column=0
                worksheet = workbook.add_worksheet("OO Code Review(Sys acct)")
                cell_format = workbook.add_format({'bold': True, 'font_color': 'green', 'bg_color': '#C0C0C0', 'border': 1})
                worksheet.set_row(0, 20)
                worksheet.set_column(0, 1, 20)
                temp1=[]
                worksheet.write(row, column, 'Name',cell_format)
                temp1.append('Name')
                column+=1
                worksheet.write(row, column, 'Path',cell_format)
                temp1.append('Path')
                self.data4.append(temp1)
                column=0
                row+=1
                for sys_acct in self.SysAccount:
                    temp1=[]
                    worksheet.write(row, column, sys_acct['name'])
                    temp1.append(sys_acct['name'])
                    column+=1
                    worksheet.write(row, column, sys_acct['path'])
                    temp1.append(sys_acct['path'])
                    self.data4.append(temp1)
                    column=0
                    row+=1

            workbook.close() 
            '''print(self.data1)
            pprint(self.data2)
            pprint(self.data3)
            pprint(self.data4)

            with open('listfile.txt', 'w') as filehandle:
                json.dump([self.data1,self.data2,self.data3,self.data4], filehandle)'''
            #If any of the table is blank
            if len(self.data1)==1:
                self.data1.append(['N/A','N/A','N/A','N/A','N/A'])
            if len(self.data2)==1:
                self.data1.append(['N/A','N/A','N/A','N/A','N/A','N/A'])
            if len(self.data3)==1:
                self.data1.append(['N/A','N/A','N/A'])
            if len(self.data4)==1:
                self.data1.append(['N/A','N/A'])
            pdf.build(self.drawPDF([self.data1,self.data2,self.data3,self.data4],colorCode))

            return fileName+extention[1],fileName+extention[0]
        else:
            return False,False

    def drawPDF(self,data,colorCode):
        flow_obj =[]
        i=0
        styles=getSampleStyleSheet()
        for tdata in data:
            if (i==0):
                styNormal = ParagraphStyle('Heading1')
                stySpaced = ParagraphStyle('spaced',parent=styNormal,alignment=TA_CENTER,spaceBefore=12,spaceAfter=12,textColor='green',fontSize=30)
                t1=Paragraph("OO Code Review Report",style=stySpaced)
                flow_obj.append(t1)
                t1=Paragraph("<para autoLeading='off'><br/><br/></para>",style=stySpaced)
                flow_obj.append(t1)
                t=Table(tdata,colWidths=[180,180,180,180,180]) 
                tstyle=TableStyle([("GRID",(0,0),(-1,-1),1,colors.black),
                            ("FONT",(0,0),(4,0),"Times-Bold",30),
                            ("FONT",(0,0),(4,-1),"Times-Bold",20),
                            ('TEXTCOLOR',(0,0),(4,0),colors.green),
                            ("BACKGROUND",(0,0),(4,0),'#C0C0C0')])
                
            
                t.setStyle(tstyle)  
                flow_obj.append(t)
            elif(i==1):
                flow_obj.append(PageBreak())
                styNormal = ParagraphStyle('Heading1')
                stySpaced = ParagraphStyle('spaced',parent=styNormal,alignment=TA_CENTER,spaceBefore=12,spaceAfter=12,textColor='green',fontSize=30)
                t1=Paragraph("OO Code Review Details",style=stySpaced)
                flow_obj.append(t1)
                t1=Paragraph("<para autoLeading='off'><br/><br/></para>",style=stySpaced)
                flow_obj.append(t1)
                t=Table(tdata,colWidths=[250,140,180,300,400,400]) 
                
                colorCode.extend([("GRID",(0,0),(-1,-1),1,colors.black),
                            ("FONT",(0,0),(5,0),"Times-Bold",30),
                            ("FONT",(0,0),(5,-1),"Times-Bold",20),
                            ('TEXTCOLOR',(0,0),(5,0),colors.green),
                            ("BACKGROUND",(0,0),(5,0),'#C0C0C0')])
                tstyle=TableStyle(colorCode)
            
                t.setStyle(tstyle)  
                flow_obj.append(t)
            elif(i==2): 
                flow_obj.append(PageBreak())
                styNormal = ParagraphStyle('Heading1')
                stySpaced = ParagraphStyle('spaced',parent=styNormal,alignment=TA_CENTER,spaceBefore=12,spaceAfter=12,textColor='green',fontSize=30)
                t1=Paragraph("OO Code Review(System properties)",style=stySpaced)
                flow_obj.append(t1)
                t1=Paragraph("<para autoLeading='off'><br/><br/></para>",style=stySpaced)
                flow_obj.append(t1)
                t=Table(tdata,colWidths=[250,300,420])
                tstyle=TableStyle([("GRID",(0,0),(-1,-1),1,colors.black),
                            ("FONT",(0,0),(2,0),"Times-Bold",20),
                            ("FONT",(0,0),(2,-1),"Times-Bold",20),
                            ('TEXTCOLOR',(0,0),(2,0),colors.green),
                            ("BACKGROUND",(0,0),(2,0),'#C0C0C0')])
                                
            
                t.setStyle(tstyle)  
                flow_obj.append(t)
            else: 
                flow_obj.append(PageBreak())
                styNormal = ParagraphStyle('Heading1')
                stySpaced = ParagraphStyle('spaced',parent=styNormal,alignment=TA_CENTER,spaceBefore=12,spaceAfter=12,textColor='green',fontSize=30)
                t1=Paragraph("OO Code Review(System accounts)",style=stySpaced)
                flow_obj.append(t1)
                t1=Paragraph("<para autoLeading='off'><br/><br/></para>",style=stySpaced)
                flow_obj.append(t1)
                t=Table(tdata,colWidths=[250,300]) 
                tstyle=TableStyle([("GRID",(0,0),(1,-1),1,colors.black),
                            ("FONT",(0,0),(1,0),"Times-Bold",20),
                            ("FONT",(0,0),(1,-1),"Times-Bold",20),
                            ('TEXTCOLOR',(0,0),(1,0),colors.green),
                            ("BACKGROUND",(0,0),(1,0),'#C0C0C0')])
                                
            
                t.setStyle(tstyle)
                flow_obj.append(t)
            
            i+=1
        return flow_obj


    def breakLines(self,line,no):
        lenght = len(line)
        no_cp = no
        while(no<lenght):
            if(no<146):
                line = line[:no] +'\n' + line[no:]
                no = no + no_cp + 2
            else:
                line = line[:146]
                if len(line[no:]) < (no_cp-4):
                    line = line + '....'
                else:
                    line = line + '\n....'
                no = lenght
        #print(line)
        if (line.find('<') != -1):
            line.replace('<','&lt;')
        if (line.find('>') != -1):
            line.replace('>','&gt;')
        return line