'''This code is used to prepearing the end user report using code review results
@author: Code Review Automation'''

import datetime,pprint,re
'''Importing xlsxwriter library to create XLSX report'''
import xlsxwriter
'''Importing reportlab.lib library to create PDF report'''
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import LETTER
# add style
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,PageBreak,CondPageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

class Report: 
   
    # init method or constructor  
    def __init__(self, context):
        #Project name
        self.ProjectName=context['title']

        #Stats
        self.stats={}
        self.stats['Flow Count']= context['flows_count']
        self.stats['System Properties']= context['sys_props']
        self.stats['System Accounts']= context['sys_accts']
        self.stats['Error Count']= context['error_count']
        self.stats['Warning Count']= context['warning_count']

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
        self.OverallReport = []
        self.IssueReport = []
        self.WarningReport = []
        self.SystemPropsReport = []
        self.SystemAccountsReport = []


   
    # create_Report Method  
    def create_Report(self,isEnabled):
        if isEnabled:
            fileName = self.ProjectName+ ' ' +datetime.datetime.now().strftime("%m-%d-%Y %H-%M-%S")
            extention = ['.xlsx', '.pdf']
            location= 'Reports/'+fileName
            workbook = xlsxwriter.Workbook(location+extention[0])
            #canvas = Canvas(location+extention[1], pagesize=LETTER)
            #PDF
            pdf = SimpleDocTemplate(
                location+extention[1],
                pagesize=LETTER,
                topMargin=0.1*inch,
                bottomMargin=0.1*inch,
                leftMargin=0.1*inch,
                rightMargin=0.1*inch
            )
            worksheet = workbook.add_worksheet("Brief Report-Processed OO code")
            cell_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#39a88d', 'border': 1, 'font_size': 13, 'align': 'vcenter'})
            worksheet.set_row(0, 20)
            worksheet.set_column(0, 4, 30)
            
            row=0
            column=0
            temp1=['Date',datetime.date.today().strftime('%d-%m-%Y')]
            self.OverallReport.append(temp1)
            temp1=['Content Pack',self.ProjectName]
            self.OverallReport.append(temp1)
            temp2=[]
            for name,stat in self.stats.items():
                #write operation performing
                temp1=[]
                row = 0
                worksheet.write(row, column, name, cell_format)
                temp1.append(name)
                row += 1
                worksheet.write(row, column, len(stat) if isinstance(stat,list) else stat)
                temp1.append(len(stat) if isinstance(stat,list) else stat)
                column += 1
                self.OverallReport.append(temp1)
            #self.OverallReport.append(temp1)
            
            worksheet_issue = workbook.add_worksheet("Detailed Report of Errors")
            worksheet_warning=workbook.add_worksheet("Detailed Report of Warnings")
            #cell_format = workbook.add_format({'bold': True, 'font_color': 'green', 'bg_color': '#C0C0C0', 'border': 1})
            worksheet_issue.set_row(0, 20)
            worksheet_warning.set_row(0, 20)
            worksheet_issue.set_column(0, 5, 35)
            worksheet_warning.set_column(0, 5, 35)
            row= 0
            column= 0
            temp_headers=['Flow Step', 'Variable Type', 'Variable Name', 'Assign From (*)', 'Default Value', 'Remarks']
            worksheet_issue, column = self.writeRow(worksheet_issue,temp_headers,row,column,cell_format)
            worksheet_warning, column = self.writeRow(worksheet_warning,temp_headers,row,column,cell_format)
            #column += 1
            #worksheet.write(row, column, "UUID", cell_format)
            self.IssueReport.append(temp_headers)
            self.WarningReport.append(temp_headers)
            row += 1
            row_issue=row_warning=row
            column= 0
            column_issue=column_warning=column
            temp1=['N/A','N/A','N/A','N/A','N/A','N/A']
            worksheet_warning, column_warning = self.writeRow(worksheet_warning,temp1,row_warning,column_warning)
            worksheet_issue, column_issue = self.writeRow(worksheet_issue,temp1,row_issue,column_issue)
            #For loop starts
            for flow in self.FlowDetails:
                #Flow Inputs Start
                if len(flow['inputs']) >0:
                    for input in flow['inputs']:
                        if('violations' in input.keys() and len(input['violations']) > 0):
                            for key in input['violations']:
                                temp1=['Flow Inputs','Input Variable',input['name'],input['assign_from'],input['default_value'],self.VIOLATION_MATRIX[key]]
                                if key in self.WARNING_MATRIX:
                                    worksheet_warning, column_warning = self.writeRow(worksheet_warning,temp1,row_warning,column_warning)
                                    self.WarningReport.append(self.prepeareItem(temp1))
                                    row_warning+=1
                                else:
                                    worksheet_issue, column_issue = self.writeRow(worksheet_issue,temp1,row_issue,column_issue)
                                    self.IssueReport.append(self.prepeareItem(temp1))
                                    row_issue+=1
                #Flow Input ends
                #Flow Outputs Start
                if len(flow['outputs']) > 0:
                    for output in flow['outputs']:
                        if('violations' in output.keys() and len(output['violations']) >0):
                            for key in output['violations']:
                                temp1=['Flow Outputs','Output Variable',output['name'],output['assign_from'],'N/A',self.VIOLATION_MATRIX[key]]
                                if key in self.WARNING_MATRIX:
                                    worksheet_warning, column_warning = self.writeRow(worksheet_warning,temp1,row_warning,column_warning)
                                    self.WarningReport.append(self.prepeareItem(temp1))
                                    row_warning+=1
                                else:
                                    worksheet_issue, column_issue = self.writeRow(worksheet_issue,temp1,row_issue,column_issue)
                                    self.IssueReport.append(self.prepeareItem(temp1))
                                    row_issue+=1
                #Flow Outputs Ends
                #Step Start
                #Step Inputs Start
                if len(flow['steps']) > 0:
                    for step in flow['steps']:
                        if step['actual_var_count'] > 0:
                            for input in step['inputs']:
                                if('violations' in input.keys() and len(input['violations']) >0):
                                    for key in input['violations']:
                                        temp1=[step['name'],'Input Variable',input['name'],input['assign_from'],input['default_value'],self.VIOLATION_MATRIX[key]]
                                        if key in self.WARNING_MATRIX:
                                            worksheet_warning, column_warning = self.writeRow(worksheet_warning,temp1,row_warning,column_warning)
                                            self.WarningReport.append(self.prepeareItem(temp1))
                                            row_warning+=1
                                        else:
                                            worksheet_issue, column_issue = self.writeRow(worksheet_issue,temp1,row_issue,column_issue)
                                            self.IssueReport.append(self.prepeareItem(temp1))
                                            row_issue+=1
                #Step Inputs End
                #Step Ouput Starts
                            for output in step['outputs']:
                                if('violations' in output.keys() and len(output['violations']) > 0):
                                    for key in output['violations']:
                                        var_type= 'Flow Output Variable' if output['variable_type'] == "FLOW_OUTPUT_FIELD" else 'Output Variable'
                                        temp1=[step['name'],var_type,output['name'],output['assign_from'],'N/A',self.VIOLATION_MATRIX[key]]
                                        if key in self.WARNING_MATRIX:
                                            worksheet_warning, column_warning = self.writeRow(worksheet_warning,temp1,row_warning,column_warning)
                                            self.WarningReport.append(self.prepeareItem(temp1))
                                            row_warning+=1
                                        else:
                                            worksheet_issue, column_issue = self.writeRow(worksheet_issue,temp1,row_issue,column_issue)
                                            self.IssueReport.append(self.prepeareItem(temp1))
                                            row_issue+=1

            #For loop ends
            #System Properties
            row=0
            temp1=['Property Name', 'OO Path', 'Where it is used ']
            worksheet = workbook.add_worksheet("Analysis of System Property use")
            worksheet.set_row(0, 20)
            worksheet.set_column(0, 2, 30)
            worksheet, column = self.writeRow(worksheet,temp1,row,column,cell_format)
            self.SystemPropsReport.append(temp1)
            if(len(self.SysProp) > 0):
                row+=1
                for sys_prop in self.SysProp:
                    if len(sys_prop['usage'])>0:
                        for used_flow in sys_prop['usage']:
                            temp1=[sys_prop['name'],sys_prop['path'],used_flow]
                            worksheet, column = self.writeRow(worksheet,temp1,row,column)
                            self.SystemPropsReport.append(self.prepeareItem(temp1))
                            row+=1
                    else:
                        temp1=[sys_prop['name'],sys_prop['path'],'not used']
                        worksheet, column = self.writeRow(worksheet,temp1,row,column)
                        self.SystemPropsReport.append(self.prepeareItem(temp1))
                        row+=1
            else:
                row+=1
                temp1=['N/A','N/A','N/A']
                worksheet, column = self.writeRow(worksheet,temp1,row,column)
            #System Accounts
            row=0
            worksheet = workbook.add_worksheet("Analysis of System Account use")
            worksheet.set_row(0, 20)
            worksheet.set_column(0, 1, 30)
            temp1=['Account Name','OO Path']
            worksheet, column = self.writeRow(worksheet,temp1,row,column,cell_format)
            self.SystemAccountsReport.append(temp1)
            if len(self.SysAccount) >0:
                row+=1
                for sys_acct in self.SysAccount:
                    temp1=[sys_acct['name'],sys_acct['path']]
                    worksheet, column = self.writeRow(worksheet,temp1,row,column)
                    self.SystemAccountsReport.append(self.prepeareItem(temp1))
                    row+=1
            else:
                row+=1
                temp1=['N/A','N/A']
                worksheet, column = self.writeRow(worksheet,temp1,row,column)

            workbook.close()
            #If any of the table is blank
            if len(self.OverallReport)==1:
                self.OverallReport.append(['N/A','N/A'])
            if len(self.IssueReport)==1:
                self.IssueReport.append(['N/A','N/A','N/A','N/A','N/A','N/A'])
            if len(self.WarningReport)==1:
                self.WarningReport.append(['N/A','N/A','N/A','N/A','N/A','N/A'])
            if len(self.SystemPropsReport)==1:
                self.SystemPropsReport.append(['N/A','N/A','N/A'])
            if len(self.SystemAccountsReport)==1:
                self.SystemAccountsReport.append(['N/A','N/A'])
            pdf.build(self.drawPDF([self.OverallReport,self.IssueReport,self.WarningReport,self.SystemPropsReport,self.SystemAccountsReport]))

            return fileName+extention[1],fileName+extention[0]
        else:
            return False,False

    def writeRow(self,docRef,ItemsToWrite,row=0,column=0,format=None):
        for item in ItemsToWrite:
            docRef.write(row, column, item,format)
            column+=1
        column=0
        
        return docRef,column

    def prepeareItem(self,ChildItem):
        ItemToAdd=[]
        for item in ChildItem:
            ItemToAdd.append(self.breakLines(item))
        return ItemToAdd

    def drawPDF(self,data):
        flow_obj =[]
        i=0
        styles=getSampleStyleSheet()
        space_3=Paragraph("<para autoLeading='off'><br/><br/></para>",style=styles['Heading1'])
        styNormal = ParagraphStyle('Heading1')
        stySmall = ParagraphStyle('spacedSmall',parent=styNormal,alignment=TA_LEFT,textColor='black',fontSize=8)
        stySpaced = ParagraphStyle('spaced',parent=styNormal,alignment=TA_LEFT,textColor='#39a88d',fontSize=13)
        stySpacedHeading = ParagraphStyle('spacedHeading',parent=styNormal,alignment=TA_CENTER,textColor='#39a88d',fontSize=16)
                
        for tdata in data:
            if (i==0):
                t1=Paragraph("<para autoLeading='off'><u><b>OO Code Review Report</b></u><br/><br/><br/></para>",style=stySpacedHeading)
                flow_obj.append(t1)
                t1=Paragraph("Brief Report of Processed OO Code:<br/><br/>",style=stySpaced)
                flow_obj.append(t1)
                '''t1=Paragraph(f"<para autoLeading='off'><br/> \
                    <font color='blue'>Date:</font> {datetime.date.today()}<br/> \
                    <font color='blue'>Content Pack:</font> {self.ProjectName}<br/> \
                    <font color='blue'>No. of Flow processed:</font> {tdata[1][0]}<br/> \
                    <font color='blue'>No. of System Account processed:</font> {tdata[1][1]}<br/> \
                    <font color='blue'>No. of System Property processed:</font> {tdata[1][2]}<br/> \
                    <font color='blue'>Error Count:</font> <b>{tdata[1][3]}</b><br/> \
                    <font color='blue'>Warning Count:</font> <b>{tdata[1][4]}</b> \
                    </para>" \
                ,style=styNormal)

                flow_obj.append(t1)'''
                colWidth= ((LETTER[0]-(0.35*inch))/5)
                t=Table(tdata,colWidths=colWidth,hAlign='LEFT') 
                tstyle=TableStyle([
                            ("GRID",(0,0),(-1,-1),0.8,"#8c8f8f"),
                            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                            ("FONT",(1,0),(1,4),"Helvetica",10),
                            ("INNERGRID",(0,0),(0,-1),0.7,colors.white),
                            ("FONT",(0,0),(0,6),"Helvetica-Bold",10),
                            ("TEXTCOLOR",(0,0),(0,-1),colors.white),
                            ("BACKGROUND",(0,0),(0,-1),"#39a88d"),
                            ("FONT",(1,5),(1,6),"Helvetica-Bold",10)])
                
            
                t.setStyle(tstyle)  
                flow_obj.append(t)
            elif(i==1):
                flow_obj.append(space_3)
                flow_obj.append(CondPageBreak(1.4*inch))
                #flow_obj.append(PageBreak())
                t1=Paragraph("Detailed Report of Error Found in Flow Steps:",style=stySpaced)
                flow_obj.append(t1)
                t1=Paragraph("<para autoLeading='off'><br/><i>* Blank column denotes value is <b>not assigned</b> to variable.</i><br/><br/></para>",style=stySmall)
                flow_obj.append(t1)
                colWidth= ((LETTER[0]-(0.35*inch))/6)
                t=Table(tdata,colWidths=colWidth)
                tstyle=TableStyle([
                            ("GRID",(0,0),(5,-1),0.7,"#8c8f8f"),
                            ("INNERGRID",(0,0),(5,0),0.7,colors.white),
                            ("FONT",(0,0),(5,0),"Helvetica-Bold",10),
                            ("TEXTCOLOR",(0,0),(5,0),colors.white),
                            ("BACKGROUND",(0,0),(5,0),"#39a88d"),
                            ("VALIGN",(0,0),(5,0),"MIDDLE"),
                            ("FONT",(0,1),(5,-1),"Helvetica",8)])
            
                t.setStyle(tstyle)  
                flow_obj.append(t)

            elif(i==2):
                flow_obj.append(space_3)
                flow_obj.append(CondPageBreak(1.4*inch))
                #flow_obj.append(PageBreak())
                t1=Paragraph("Detailed Report of Warning Found in Flow Steps:",style=stySpaced)
                flow_obj.append(t1)
                t1=Paragraph("<para autoLeading='off'><br/><i>* Blank column denotes value is <b>not assigned</b> to variable.</i><br/><br/></para>",style=stySmall)
                flow_obj.append(t1)
                colWidth= ((LETTER[0]-(0.35*inch))/6)
                t=Table(tdata,colWidths=colWidth)
                tstyle=TableStyle([
                            ("GRID",(0,0),(5,-1),0.7,"#8c8f8f"),
                            ("INNERGRID",(0,0),(5,0),0.7,colors.white),
                            ("FONT",(0,0),(5,0),"Helvetica-Bold",10),
                            ("TEXTCOLOR",(0,0),(5,0),colors.white),
                            ("BACKGROUND",(0,0),(5,0),"#39a88d"),
                            ("VALIGN",(0,0),(5,0),"MIDDLE"),
                            ("FONT",(0,1),(5,-1),"Helvetica",8)])
            
                t.setStyle(tstyle)  
                flow_obj.append(t)

            elif(i==3):
                flow_obj.append(space_3)
                flow_obj.append(CondPageBreak(1.4*inch))
                #flow_obj.append(PageBreak())
                t1=Paragraph("Analysis of System Property Used:<br/><br/>",style=stySpaced)
                flow_obj.append(t1)
                colWidth= ((LETTER[0]-(0.35*inch))/3)
                t=Table(tdata,colWidths=colWidth)
                tstyle=TableStyle([
                            ("GRID",(0,0),(2,-1),0.7,"#8c8f8f"),
                            ("INNERGRID",(0,0),(2,0),0.7,colors.white),
                            ("FONT",(0,0),(2,0),"Helvetica-Bold",10),
                            ("TEXTCOLOR",(0,0),(2,0),colors.white),
                            ("BACKGROUND",(0,0),(2,0),"#39a88d"),
                            ("VALIGN",(0,0),(2,0),"MIDDLE"),
                            ("FONT",(0,1),(2,-1),"Helvetica",8)])
                                
            
                t.setStyle(tstyle)  
                flow_obj.append(t)
            else:
                flow_obj.append(space_3)
                flow_obj.append(CondPageBreak(1.4*inch))
                #flow_obj.append(PageBreak())
                t1=Paragraph("Analysis of System Account Used:<br/><br/>",style=stySpaced)
                flow_obj.append(t1)
                colWidth= ((LETTER[0]-(0.35*inch))/2)
                t=Table(tdata,colWidths=colWidth) 
                tstyle=TableStyle([
                            ("GRID",(0,0),(1,-1),0.7,"#8c8f8f"),
                            ("INNERGRID",(0,0),(1,0),0.7,colors.white),
                            ("FONT",(0,0),(1,0),"Helvetica-Bold",10),
                            ("TEXTCOLOR",(0,0),(1,0),colors.white),
                            ("BACKGROUND",(0,0),(1,0),"#39a88d"),
                            ("VALIGN",(0,0),(1,0),"MIDDLE"),
                            ("FONT",(0,1),(1,-1),"Helvetica",8)])
                                
            
                t.setStyle(tstyle)
                flow_obj.append(t)
            
            i+=1
        return flow_obj


    def breakLines(self,line,no=None):
        '''lenght = len(line)
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
                no = lenght'''
        if len(line)>300:
            line=line[:300] + ' ...'
        if line !='<not assigned>':
            if '<' in line:
                line=line.replace('<','&lt;')
            if '>' in line:
                line=line.replace('>','&gt;')
        else:
            line=''
        styles=getSampleStyleSheet()
        innerContent= ParagraphStyle('innerContent',fontName='Helvetica',fontSize=8)
        line=Paragraph(line,style=innerContent)
        return line
