"""
This .py file contains the work Rebecca Duke Weisenberg 
and Reid Harris did to incorporate language fields and the one
year guideline fields to the ocr.

They are to be incorporated since our group ran out of time.
"""


class Language_fields:
    def get_applicant_indigenous_status(self) -> str:
        '''
        • If the term "indigenous" appears in the document, the field will return 
        the name of asylum seeker's tribe/nation/group. Cuurently, the field will return 
        the two tokens that precede "indigenous;" this method needs to be fine-tuned and 
        validated.
        '''
        indigenous: List[str]
        indigenous = [
            'indigenous'
        ]

        similar_indig: Callable[[str, float], Union[str, None]]
        similar_indig = similar_in_list(indigenous)

        for token in self.doc:

            sent: str
            sent = token.sent.text.lower()

            s: Union[str, None]
            s = similar_indig(token.text.lower(), 0.9)

            if s == 'indigenous group':
                prev_wrds = self.doc[[token.i-1, token.i-2]].text.lower()
                # return the name of the specific group/nation
                return prev_wrds   

    def get_applicant_language(self) -> str:
        '''
        • If the term "native speaker" appears in the document, the field will return 
        the asylum seeker's stated native language. Cuurently, the field will return 
        the two tokens that precede "native speaker;" this method needs to be fine-tuned and 
        validated.
        '''
        for token in self.doc:

            sent: str
            sent = token.sent.text.lower()

            s: Union[str, None]
            s = similar_pg(token.text.lower(), 0.9)

            if s == 'native speaker' or s == 'native speakers':
                next_wrds = self.doc[[token.i+1, token.i+2]].text.lower()
                return next_wrds
        
        return 'Ability to testify in English' 

    def get_applicant_access_interpeter(self) -> str:
        '''
        • If the terms "interpreter" or "translator" appear in the document, 
        the field will return whether the asylum seeker had access to an 
        interpreter during their hearings. Curently, the field's output is 
        dependent on occurance of specific tokens in the document; this method 
        needs to be fine-tuned and validated.
        '''
        for token in self.doc:

            sent: str
            sent = token.sent.text.lower()

            s: Union[str, None]
            s = similar_pg(token.text.lower(), 0.9)

            if s == 'interpreter' or s == 'translator':
                surrounding: Span
                surrounding = self.get_surrounding_sents(token)

                next_word = self.doc[token.i+1].text.lower()
                if 'requested' in surrounding.text.lower() \
                    and 'granted' in surrounding.text.lower(): 
                    return 'Had access'
                elif 'requested' in surrounding.text.lower() \
                    and 'was present' in surrounding.text.lower(): 
                    return 'Yes'
                elif 'requested' in surrounding.text.lower() \
                    and 'granted' not in surrounding.text.lower(): 
                    return 'No'
                elif 'requested' in surrounding.text.lower() \
                    and 'was present' in surrounding.text.lower(): 
                    return 'No'

    def get_applicant_determined_credibility(self) -> str:
        '''
        • Returns the judge's decision on whether the applicant is a credible witness.
        Curently, the field's output is dependent on occurance of specific tokens 
        in the document; this method needs to be fine-tuned and validated.
        '''

        credibility = [
            'credible'
        ]

        similar_cred: Callable[[str, float], Union[str, None]]
        similar_cred = similar_in_list(credibility)

        for token in self.doc:

            sent: str
            sent = token.sent.text.lower()

            s: Union[str, None]
            s = similar_cred(token.text.lower(), 0.9)

            if s == 'credible':
                prev_word = self.doc[token.i-1].text.lower()
                next_word = self.doc[token.i+1].text.lower()
                if not similar(prev_word, 'not', 0.95) \
                    and not similar(next_word, 'witness', 0.95): 
                    return 'Yes'
                else:
                    return 'No'
                if s not in self.doc:
                    return 'N/A to case'


"""
These would be added to ocr.py
"""

    ### Getting applicant's indigenous status
    indigenous_status = case.get_applicant_indigenous_status()
    case_data['is_applicant_indigenous'] = indigenous_status

    ### Getting applicant's native language
    applicant_lang = case.get_applicant_language()

    case_data['applicant_language'] = applicant_lang

    ### Getting ability to access interpreter
    access_to_interpreter = case.get_applicant_access_interpeter()
    case_data['applicant_access_to_interpreter'] = access_to_interpreter

        ### Getting applicant's credibility status
    determined_applicant_credibility = case.get_applicant_determined_credibility()

    case_data['determined_applicant_credibility'] = determined_applicant_credibility

"""
This is the work done by reid harris to add the one_year_guideline field
We ran out of time and were not able to incorporate this method to the API
More info on his work can be found in the notebook OneYearLimit.py
"""

class one_year_guideline:
    def check_for_one_year(self) -> bool:
        """
        Checks whether or not the asylum-seeker argued to be exempt from the
        one-year guideline.  Specifically, it checks to see if the document
        contains either "changed circumstance" or "extraordinary circumstance". 
        If it does, and one of the five terms ("year", "delay", "time",
        "period", "deadline") is within 10 lemmas, then the function
        returns True.  Otherwise, it returns False.
        """
        # If one of the four context words are w/in 100 characters of the
        # phrase, we conclude that it is related to the one-year rule
        lemma_list = [token.lemma_.lower() for token in self.doc]
        for idx in range(0,len(lemma_list)):
            if (lemma_list[idx] == 'change') \
                & (lemma_list[idx + 1] == 'circumstance'):
                idx_start = lemma_list.index('change')
                idx_end  = idx_start + 1
                search_list = [lemma for lemma in \
                    lemma_list[idx_start - 10: idx_end + 10]]
                if any(term in search_list \
                    for term in ('year','delay','time','period','deadline')):
                    return True
        # Do the same for "extraordinary circumstance"
        for idx in range(0,len(lemma_list)):
            if (lemma_list[idx] == 'extraordinary') \
                & (lemma_list[idx + 1] == 'circumstance'):
                idx_start = lemma_list.index('change')
                idx_end  = idx_start + 1
                search_list = [lemma for lemma in \
                    lemma_list[idx_start - 10: idx_end + 10]]
                if any(term in search_list for term in \
                    ('year','delay','time','period','deadline')):
                    return True
        return False
""" 
Something like this would be added to ocr.py
"""
    ## Getting whether the case argued against the one-year guideline
    case_data['one_year_guideline'] = f'{case.check_for_one_year()}'
