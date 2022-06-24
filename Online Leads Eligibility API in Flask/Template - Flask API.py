_version__ = '0.0.1'
__author__ = 'Ishan Jain
__lastupdate__ = '2022'

"""
API is used for assessing Online Leads Eligibility. 

Online Leads are generated through facebook and Google Ads. 

"""

from flask import Blueprint, request, jsonify
import pandas as pd
import requests
import bs4
from bs4 import BeautifulSoup
from utilities import api_validation_function as avf
from los import los_function as lf


# Define blueprint
online_leads_eligibility_api = Blueprint('online_leads_eligibility_api', __name__)


@online_leads_eligibility_api.route("/los/v1/online_leads_eligibility_api", methods=['POST'])
def online_leads_eligibility():
    
    """
       @api {POST} /los/v1/online_leads_eligibility_api
       @apiName online leads eligibility
       @apiGroup los
       @apiVersion 0.0.1
       
       
    """
       
    # defining a variable api_name for later usage
    api_name = "los/v1/online_leads_eligibility"
    
    # ----------------------------------------------------------------
    # Step 1.1 - API request method check - Only POST is allowed
    # ----------------------------------------------------------------
    if request.method != "POST":
        return_response = default_api_response_dict(request_status = "fail", 
                                                    request_message = "invalid API request method", 
                                                    online_leads_eligibility_status = "NA", 
                                                    body_message = "NA", 
                                                    error_response_code = 'NA')
        return return_response

    # taking the request data in a seperate variable for further usage
    request_data = request.form
    
    
    #====================================================================================
    # Step 2 - Token authentication
    #====================================================================================
    token_valid_flag = avf.validate_token_and_api_access(request_data, api_name)

    # logs
    message = f"Token authentication"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    if token_valid_flag['status'] == "fail":
        return_response = default_api_response_dict(request_status = "fail", 
                                                    request_message = token_valid_flag['error'], 
                                                    online_leads_eligibility_status = "NA", 
                                                    body_message = "NA", 
                                                    error_response_code = 'NA')

        avf.add_api_call_hist_data(api_name,
                                   api_error_label="token", 
                                   api_status="success", 
                                   logic_status="fail", 
                                   api_request = request_data,
                                   api_response = return_response)

        return return_response
    
    #====================================================================================
    # Step 3 - Check all mandatory params in request data
    #====================================================================================

    # logs
    message = f"Check all mandatory params in request data"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    mandatory_param_lst = ['application_id',
                          'business_name',
                          'business_pincode',
                          'mobile_number',
                          'business_type',
                          'business_main_sector',
                          'business_specific_sector',
                          'vintage_months',
                          'average_annual_turnover',
                          'required_loan_amount',
                          'preferred_monthly_EMI',
                          'applicant_name',
                          'app_highmark_score_A8']

    optional_param_lst = ['loan_purpose',
                          'applicant_pan_number',
                          'email_address',
                          'email_type',
                          'dev_bypass',
                          'loan_type',
                          'applicant_highmark_XML']
    
    all_params_status = avf.check_required_parameter(request_data, mandatory_param_lst)

    if all_params_status == False:
        return_response = default_api_response_dict(request_status = "fail", 
                                                    request_message = "all mandatory parameters are not sent", 
                                                    online_leads_eligibility_status = "NA", 
                                                    body_message = "NA", 
                                                    error_response_code = 'NA')

        avf.add_api_call_hist_data(api_name,
                                   api_error_label="missing mandatory parameter", 
                                   api_status="success", 
                                   logic_status="fail", 
                                   api_request = request_data,
                                   api_response = return_response)

        return return_response
    
    
    #====================================================================================
    # Step-4 If dev_bypass is True, return success
    #====================================================================================

    # logs
    message = f"If dev_bypass is True, return success"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    if 'dev_bypass' in request_data.keys():
        if request_data['dev_bypass'].lower() == 'true':
            return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = "successfully completed API call", 
                                                        online_leads_eligibility_status = "success", 
                                                        body_message = "DEV_BYPASS -> online_leads_eligibility process has been by-passed successfully", 
                                                        error_response_code = 'NA')

            avf.add_api_call_hist_data(api_name,
                                    api_error_label=f"NA",
                                    api_status="success",
                                    logic_status="success",
                                    api_request = request_data,
                                    api_response = return_response)

            return return_response
        

    #====================================================================================
    # Step-5 Check data type for all numeric parameters
    #====================================================================================

    # logs
    message = f"Check data type for all numeric parameters"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    numeric_param_lst = ['vintage_months',
                         'average_annual_turnover', 
                         'required_loan_amount', 
                         'preferred_monthly_EMI',
                         'business_pincode'] 
    
    # business_mobile is not considered into this list.

    for param in numeric_param_lst:
        try:
            float(request_data[param])
        except:
            return_response = default_api_response_dict(request_status = "fail", 
                                                        request_message = f"Parameter {param} should be numeric",
                                                        online_leads_eligibility_status = "NA", 
                                                        body_message = 'NA', 
                                                        error_response_code = 'NA')

            avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"{param} data type", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)

            return return_response


    #====================================================================================
    # Step-6 Check non negative parameters out of all numeric parameters
    #====================================================================================

    # logs
    message = f"Check non negative parameters out of all numeric parameters"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    non_negative_param_lst =  ['vintage_months',
                               'average_annual_turnover', 
                               'required_loan_amount', 
                               'preferred_monthly_EMI',
                               'business_pincode'] 

    for param in non_negative_param_lst:
        if float(request_data[param]) < 0:
            return_response = default_api_response_dict(request_status = "fail", 
                                                        request_message = f"Parameter {param} should not be negative", 
                                                        online_leads_eligibility_status = "NA", 
                                                        body_message = "NA", 
                                                        error_response_code = 'NA')

            avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"{param} negative", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)

            return return_response
        
    #====================================================================================
    # Step-7 Get threshold variables required
    #====================================================================================

    message = 'Get threshold variables required for online leads eligibility API from "los_thresholds" table in dsapi schema...'
    avf.make_log(message=message, api_name=api_name, request_data=request_data)
    
    threshold_df = lf.get_env_variables(api_name)
    
    message = f'Thresholds required for this api --> {threshold_df}'
    avf.make_log(message=message, api_name=api_name, request_data=request_data)
    
    # vintage upperbound and lower bound.
    min_vintage = int(threshold_df.loc[threshold_df.var_key == 'MIN_VINTAGE',"var_value"].values[0])
    max_vintage = int(threshold_df.loc[threshold_df.var_key == 'MAX_VINTAGE',"var_value"].values[0])

    # reading turnover upper and lower bound.
    min_turnover = int(threshold_df.loc[threshold_df.var_key == 'MIN_TURNOVER',"var_value"].values[0])
    max_turnover = int(threshold_df.loc[threshold_df.var_key == 'MAX_TURNOVER',"var_value"].values[0])

    # loan amount upper and lower bound.
    min_loan_amount = int(threshold_df.loc[threshold_df.var_key == 'MIN_LOAN_AMOUNT',"var_value"].values[0])
    max_loan_amount = int(threshold_df.loc[threshold_df.var_key == 'MAX_LOAN_AMOUNT',"var_value"].values[0])

    # Min and Max eligible CRIF score for the applicant.
    min_crif_score = int(threshold_df.loc[threshold_df.var_key == 'MIN_CRIF_SCORE',"var_value"].values[0])
    max_crif_score = int(threshold_df.loc[threshold_df.var_key == 'MAX_CRIF_SCORE',"var_value"].values[0])
    
    
    #====================================================================================
    # Step-8 Online Leads eligibility CHECK 1 - Business Pincode Service-abiltiy
    #====================================================================================
    # logs
    message = f"Step-8 Online Leads eligibility CHECK 1 - Business Pincode Eligibility"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    business_pincode = (request_data['business_pincode'])
    
    
    if len(business_pincode) >= 7:
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"entered pincode is wrong", 
                                                        error_response_code = 'NA')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"entered pincode is wrong", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)

        return return_response
    
    # Fetch Business Pincode from the Pincode Eng API
    # "Check_Pincode" function in "Loan_Function.py" will return True or False
    is_pincode = lf.check_pincode(business_pincode, request_data=request_data,api_name=api_name)
    
    if not is_pincode:
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "NA", 
                                                        body_message = f"Non Serviceable Pin-code", 
                                                        error_response_code = '252')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Non Serviceable Pin-code", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)

        return return_response

    
    #====================================================================================
    # Step-9 Online Leads eligibility CHECK 2 - Sector Validity 
    #====================================================================================
    # logs
    message = f"Step-9 Online Leads eligibility CHECK 2 - Sector Validity"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    business_main_sector = request_data['business_main_sector']
    business_type = request_data['business_type']
    
    # validating sector and the fucntion returns True or False
    is_sector = lf.validate_sector(business_main_sector, business_type)
    
    if not is_sector:
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"Excluded Sector", 
                                                        error_response_code = '253')
        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Excluded Sector", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)
        return return_response    



    #====================================================================================
    # Step-10 Online Leads eligibility CHECK 3 - Sub-Sector Validity 
    #====================================================================================
    # logs
    message = f"Step-10 Online Leads eligibility CHECK 3 - Sub-Sector Validity"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    business_main_sector = request_data['business_main_sector']
    business_specific_sector = request_data['business_specific_sector']
    business_type = request_data['business_type']
    
    # validating sub-sector it return True or False
    is_subsector = lf.validate_subsector(business_main_sector, business_type, business_specific_sector)

    if is_subsector:
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"Excluded Sub-Sector", 
                                                        error_response_code = '254')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Excluded Sub-Sector", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)

        return return_response 
    
    #===========================================================================================================
    # Step-11 Online Leads eligibility CHECK 4 - Vintage Check for the given business with "business_type"
    #===========================================================================================================
    # logs
    message = f"Step-11 Online Leads eligibility CHECK 4 - Vintage Check for the given business"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    business_type = (request_data['business_type']).lower()
    vintage_months = int(request_data['vintage_months'])
    
    if ((business_type == "manufacturing") & (vintage_months < min_vintage)) | ((business_type in ['trading', 'services']) & (vintage_months < max_vintage)):
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"Low vintage", 
                                                        error_response_code = '255')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Low vintage", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)

        return return_response 



    #====================================================================================
    # Step-12 Online Leads eligibility CHECK 5 - Annual Business Turnover check
    #====================================================================================
    # logs
    message = f"Step-12 Online Leads eligibility CHECK 5 - Annual Business Turnover check"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    average_annual_turnover = int(request_data['average_annual_turnover'])
    
    # annual turnover amount validation here it should be
    # >6L and <18Cr.
    if ((average_annual_turnover < min_turnover) | (average_annual_turnover > max_turnover)):
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"Low Annual Business Turnover", 
                                                        error_response_code = '256')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Low Annual Business Turnover", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)

        return return_response 

    
    #====================================================================================
    # Step-13 Online Leads eligibility CHECK 6 - requested loan amount validation 
    #====================================================================================
    # logs
    message = f"Step-13 Online Leads eligibility CHECK 6 - requested loan amount validation"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    required_loan_amount = int(request_data['required_loan_amount'])
    
    # requested loan amount validation here it should be
    # >50K and <30L.
    if ((required_loan_amount < min_loan_amount) | (required_loan_amount > max_loan_amount)):
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"Loan Amount not in Range", 
                                                        error_response_code = '257')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Loan Amount not in Range", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)
        return return_response 


    #====================================================================================
    # Step-14 Online Leads eligibility CHECK 7 - Highmark Score Check
    #====================================================================================
    # logs
    message = f"Step-14 Online Leads eligibility CHECK 7 - Highmark Score Check"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    app_highmark_score_A8 = int(request_data['app_highmark_score_A8'])
    
    if ((app_highmark_score_A8 < max_crif_score) & (app_highmark_score_A8 > min_crif_score)):
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"Highmark Score is not as per the loan policy", 
                                                        error_response_code = '258')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Highmark Score is not as per the loan policy", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)
        return return_response     
    

    #====================================================================================
    # Step-15 Online Leads eligibility CHECK 8 - Loan Purpose
    #====================================================================================
    # logs
    message = f"Step-15 Online Leads eligibility CHECK 8 - Loan Purpose"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)
    
    loan_purpose = "missing"
    
    if 'loan_purpose' in list(request_data.keys()):
        loan_purpose = str(request_data['loan_purpose'])
        
    loan_purpose = loan_purpose.lower()
    loan_purpose = loan_purpose.replace(" ", "_")
    
    if ((loan_purpose == "machine_purchase") | (loan_purpose == "asset_purchase")):
        message = f"Step 15 - Non Serviceable Loan Purpose"
        avf.make_log(request_data=request_data, message=message,api_name=api_name)
        
        return_response = default_api_response_dict(request_status = "success", 
                                                        request_message = 'successfully completed API call', 
                                                        online_leads_eligibility_status = "fail", 
                                                        body_message = f"Non Serviceable Loan Purpose", 
                                                        error_response_code = '251')

        avf.add_api_call_hist_data(api_name,
                                       api_error_label=f"Non Serviceable Loan Purpose", 
                                       api_status="success", 
                                       logic_status="fail", 
                                       api_request = request_data,
                                       api_response = return_response)
        return return_response     
        
    
    #====================================================================================
    # Step-16 Online Leads eligibility CHECK 9 - Highmark XML Extraction
    #====================================================================================
    # # Get the url of the B2C CRIF report in the XML format   
    # applicant_highmark_XML = str(request_data['applicant_highmark_XML'])
    # # sample_url = 'https://kinara-staging.autonom8.com/gcs/asia.a8flowapps.autonom8.com/kinara/assets/86a964f4-7a5e-4369-bb7c-9598996c711b'

    # # read the XML URL using requests 
    # b2c_xml = requests.get(applicant_highmark_XML)

    # # convert the content of the URL into soup object using HTML parser
    # soup= BeautifulSoup(b2c_xml.content,"html.parser")

    # # get score-value tag from the HTML 
    # print(soup.find("score-value"))

    # # get score value in Integer from the Content of the "score-value" tag 
    # extracted_score = (int(float(soup.find("score-value").contents[0])))
    
    
    
    
    #====================================================================================
    # Step-16 All checks are completed - Success response - customer eligible
    #====================================================================================

    # logs
    message = f"All checks are completed - Success response"
    avf.make_log(request_data=request_data, message=message, api_name=api_name)

    return_response = default_api_response_dict(request_status = "success", 
                                                request_message = "successfully completed API call", 
                                                online_leads_eligibility_status = "success", 
                                                body_message = "online leads eligibility process completed successfully", 
                                                error_response_code = 'NA')

    avf.add_api_call_hist_data(api_name,
                               api_error_label=f"NA",
                               api_status="success",
                               logic_status="success",
                               api_request = request_data,
                               api_response = return_response)

    return return_response


#====================================================================================
# All the Functions used
#====================================================================================
def default_api_response_dict(request_status, 
                              request_message, 
                              online_leads_eligibility_status, 
                              body_message, 
                              error_response_code):             
    '''Function returns a dictionary with api output parameters.
    Function is called whenever the api response dict is to be sent'''

    api_response_dict = {
                            'request_status': request_status,
                            'request_message': request_message,
                            'body': {
                                        'online_leads_eligibility_status': online_leads_eligibility_status, 
                                        'body_message': body_message,
                                        'error_response_code': error_response_code
                                    }
                        }
    
    return api_response_dict
