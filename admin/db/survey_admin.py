#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017-2018
from flask_security.utils import encrypt_password
from sqlalchemy.exc import IntegrityError

from models import (db, user_datastore, MobileCoordinate, MobileUser, PromptQuestion,
                    PromptQuestionChoice, PromptResponse, Survey, SurveyQuestion, SurveyResponse,
                    SurveyQuestionChoice)
from hardcoded_survey_questions import default_stack


class SurveyAdminActions:
    def names(self):
        return [n for n, in Survey.query.with_entities(Survey.pretty_name).order_by(Survey.name).all()]

    def get_user_role(self, role):
        return user_datastore.find_or_create_role(name=role)

    def _create_admin(self, survey, email, password):
        admin_role = self.get_user_role('admin')
        user = user_datastore.create_user(
            email=email,
            password=encrypt_password(password),
            survey_id=survey.id)
        user_datastore.add_role_to_user(user, admin_role)
        return user

    def get_admin(self, survey):
        admin_role = self.get_user_role('admin')
        for user in survey.web_users:
            for role in user.roles:
                if role == admin_role:
                    return user

    def get_admin_email(self, survey):
        admin = self.get_admin(survey)
        if admin:
            return admin.email

    def _generate_multicolumn_index(self, survey):
        searchable_field_ids = (1, 2, 3, 5, 6, 100, 101, 102,
                                103, 104, 108, 109, 110, 111)
        query = survey.survey_questions
        answers_columns = [q.question_label for q in query.all()
                           if q.question_type in searchable_field_ids]

        if answers_columns:
            # create a new multi-index for full-text search
            index_fields = []
            for col in answers_columns:
                index_fields.append(db.func.lower(SurveyResponse.response[col].astext))

            new_index = db.Index('survey{}_multi_idx'.format(survey.id), *index_fields)
            new_index.create(bind=db.engine)
            db.session.flush()

    def _load_survey_questions(self, survey, questions):
        # remove old survey questions
        survey.survey_questions.delete(synchronize_session=False)
        db.session.flush()

        # load hardcoded default questions to new survey
        for question_index, question in enumerate(questions):
            survey_question = SurveyQuestion(
                survey_id=survey.id,
                question_num=question_index,
                question_type=question['id'],
                question_label=question['colName'],
                question_text=question['prompt'])

            for field_name, field_value in question['fields'].items():
                # ignore non-english (default) field names
                if 'choices_' in field_name:
                    continue

                if field_name == 'choices':
                    # use integer (list index) value for hardcoded
                    # question responses instead of text-values (iOS app request);
                    # this has a reciprocal reverse-lookup in the mobile api
                    if question['id'] >= 100:
                        for choice_index, choice_text in enumerate(field_value):
                            question_choice = SurveyQuestionChoice(
                                choice_num=choice_index,
                                choice_text=choice_index,
                                choice_field='option')
                            survey_question.choices.append(question_choice)

                    else:
                        for choice_index, choice_text in enumerate(field_value):
                            question_choice = SurveyQuestionChoice(
                                choice_num=choice_index,
                                choice_text=choice_text,
                                choice_field='option')
                            survey_question.choices.append(question_choice)
                else:
                    question_choice = SurveyQuestionChoice(
                        choice_num=None,
                        choice_text=field_value,
                        choice_field=field_name)
                    survey_question.choices.append(question_choice)
            db.session.add(survey_question)
        db.session.flush()
        self._generate_multicolumn_index(survey)

    def _load_survey_prompts(self, survey, prompts):
        for prompt_index, prompt in enumerate(prompts):
            prompt_question = PromptQuestion(survey_id=survey.id,
                                             prompt_num=prompt_index,
                                             prompt_type=prompt['id'],
                                             prompt_label=prompt['colName'],
                                             prompt_text=prompt['prompt'])
            for choice_index, choice_text in enumerate(prompt['fields']['choices']):
                question_choice = PromptQuestionChoice(
                    prompt_id=prompt_question.id,
                    choice_num=choice_index,
                    choice_text=choice_text,
                    choice_field='option')
                prompt_question.choices.append(question_choice)
            db.session.add(prompt_question)

    def create_from_schema(self, survey_name, admin_email, admin_password,
                           language, survey_questions, survey_prompts):
        try:
            with db.session.begin_nested():
                survey = Survey(name=survey_name.lower(),
                                pretty_name=survey_name,
                                language=language)
                db.session.add(survey)

                hardcoded_questions = default_stack + survey_questions
                self._load_survey_questions(survey=survey, questions=hardcoded_questions)
                self._load_survey_prompts(survey=survey, prompts=survey_prompts)
                self._create_admin(survey, admin_email, admin_password)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return e.message

    def generate_summary(self, survey_name, start, end):
        survey = Survey.query.filter_by(name=survey_name.lower()).one_or_none()

        new_users_query = survey.mobile_users.filter(db.and_(MobileUser.created_at >= start,
                                                             MobileUser.created_at <= end))

        new_points_query = (MobileCoordinate.query
                                            .filter(db.and_(MobileCoordinate.survey_id == survey.id,
                                                            MobileCoordinate.timestamp >= start,
                                                            MobileCoordinate.timestamp <= end)))
        active_users_query = (survey.mobile_coordinates.filter(MobileCoordinate.timestamp >= start,
                                                               MobileCoordinate.timestamp <= end)
                                                       .distinct(MobileCoordinate.mobile_id))

        new_prompts_query = PromptResponse.query.filter(db.and_(PromptResponse.survey_id == survey.id,
                                                                PromptResponse.displayed_at >= start,
                                                                PromptResponse.displayed_at <= end))
        summary = {
            'new_users': new_users_query.count(),
            'active_users': active_users_query.with_entities(MobileCoordinate.mobile_id).count(),
            'num_points': new_points_query.count(),
            'num_prompts': new_prompts_query.count()
        }
        return summary
