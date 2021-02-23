-- alembic_version
CREATE TABLE alembic_version (
    version_num VARCHAR(36)
);
CREATE UNIQUE INDEX alembic_version_pkc ON alembic_version USING btree (version_num);

-- mobile_cancelled_prompt_responses
CREATE TABLE mobile_cancelled_prompt_responses (
    id            SERIAL PRIMARY KEY,
    survey_id     INTEGER NOT NULL,
    mobile_id     INTEGER NOT NULL,
    latitude      NUMERIC(10, 7),
    longitude     NUMERIC(10, 7),
    displayed_at  TIMESTAMP WITH TIME ZONE,
    cancelled_at  TIMESTAMP WITH TIME ZONE,
    is_travelling BOOLEAN,
    prompt_uuid   VARCHAR(36)
);
CREATE UNIQUE INDEX ix_mobile_cancelled_prompt_responses_prompt_uuid ON mobile_cancelled_prompt_responses USING btree (prompt_uuid);

-- mobile_coordinates
CREATE TABLE mobile_coordinates (
    id             SERIAL PRIMARY KEY,
    survey_id      INTEGER NOT NULL,
    mobile_id      INTEGER NOT NULL,
    latitude       NUMERIC(10, 7),
    longitude      NUMERIC(10, 7),
    altitude       NUMERIC(10, 6),
    speed          NUMERIC(10, 6),
    direction      NUMERIC(10, 6),
    h_accuracy     DOUBLE PRECISION,
    v_accuracy     DOUBLE PRECISION,
    acceleration_x NUMERIC(10, 6),
    acceleration_y NUMERIC(10, 6),
    acceleration_z NUMERIC(10, 6),
    mode_detected  INTEGER,
    timestamp      TIMESTAMP WITH TIME ZONE,
    point_type     INTEGER
);
CREATE INDEX mobile_coordinates_timestamp_idx ON mobile_coordinates USING btree ("timestamp");
CREATE INDEX mobile_coordinates_survey_timestamp_idx ON mobile_coordinates USING btree (survey_id, "timestamp");
CREATE INDEX mobile_coordinates_user_timestamp_idx ON mobile_coordinates USING btree(mobile_id, "timestamp");

-- mobile_prompt_responses
CREATE TABLE mobile_prompt_responses (
    id           SERIAL PRIMARY KEY,
    survey_id    INTEGER NOT NULL,
    mobile_id    INTEGER NOT NULL,
    response     JSONB,
    recorded_at  TIMESTAMP WITH TIME ZONE,
    latitude     NUMERIC(16, 10),
    longitude    NUMERIC(16, 10),
    displayed_at TIMESTAMP WITH TIME ZONE,
    prompt_uuid  VARCHAR(36),
    edited_at    TIMESTAMP WITH TIME ZONE,
    prompt_num   INTEGER NOT NULL
);
CREATE INDEX ix_mobile_prompt_responses_prompt_uuid ON mobile_prompt_responses USING btree (prompt_uuid);

-- mobile_survey_responses
CREATE TABLE mobile_survey_responses (
    id        SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL,
    mobile_id INTEGER NOT NULL,
    response  JSONB
);
CREATE UNIQUE INDEX mobile_survey_responses_mobile_id_key ON mobile_survey_responses USING btree (mobile_id);

-- mobile_users
CREATE TABLE mobile_users (
    id               SERIAL PRIMARY KEY,
    created_at       TIMESTAMP WITH TIME ZONE,
    modified_at      TIMESTAMP WITH TIME ZONE,
    survey_id        INTEGER NOT NULL,
    uuid             VARCHAR(36),
    model            VARCHAR(160),
    itinerum_version VARCHAR(16),
    os               VARCHAR(16),
    os_version       VARCHAR(16)
);
CREATE UNIQUE INDEX mobile_users_uuid_key ON mobile_users USING btree (uuid);

-- prompt_question_choices
CREATE TABLE prompt_question_choices (
    id           SERIAL PRIMARY KEY,
    prompt_id    INTEGER,
    choice_num   INTEGER,
    choice_text  VARCHAR(500),
    choice_field VARCHAR(16)
);

-- prompt_questions
CREATE TABLE prompt_questions (
    id              SERIAL PRIMARY KEY,
    survey_id       INTEGER NOT NULL,
    prompt_num      INTEGER NOT NULL,
    prompt_type     INTEGER NOT NULL,
    prompt_label    VARCHAR(100),
    prompt_text     VARCHAR(500),
    answer_required BOOLEAN
);
CREATE INDEX ix_prompt_questions_prompt_num ON prompt_questions USING btree (prompt_num);

-- statistics
CREATE TABLE statistics (
    id                       SERIAL PRIMARY KEY,
    last_stats_update        TIMESTAMP WITH TIME ZONE,
    last_survey_stats_update TIMESTAMP WITH TIME ZONE,
    last_mobile_stats_update TIMESTAMP WITH TIME ZONE,
    total_surveys            INTEGER NOT NULL DEFAULT 0
);

-- statistics_mobile_users
CREATE TABLE statistics_mobile_users (
    id                      SERIAL PRIMARY KEY,
    survey_id               INTEGER NOT NULL,
    mobile_id               INTEGER NOT NULL,
    latest_coordinate       INTEGER,
    latest_prompt           INTEGER,
    latest_cancelled_prompt INTEGER,
    total_coordinates       INTEGER,
    total_prompts           INTEGER,
    total_cancelled_prompts INTEGER
);
CREATE UNIQUE INDEX statistics_mobile_users_mobile_id_key ON statistics_mobile_users USING btree (mobile_id);

-- statistics_surveys
CREATE TABLE statistics_surveys (
    id                      SERIAL PRIMARY KEY,
    total_coordinates       INTEGER,
    total_prompts           INTEGER,
    total_cancelled_prompts INTEGER
);

-- survey_question_choices
CREATE TABLE survey_question_choices (
    id           SERIAL PRIMARY KEY,
    question_id  INTEGER NOT NULL,
    choice_num   INTEGER,
    choice_text  VARCHAR(500),
    choice_field VARCHAR(16)
);

-- survey_questions
CREATE TABLE survey_questions (
    id              SERIAL PRIMARY KEY,
    survey_id       INTEGER NOT NULL,
    question_num    INTEGER NOT NULL,
    question_type   INTEGER NOT NULL,
    question_label   VARCHAR(100),
    question_text   VARCHAR(500),
    answer_required BOOLEAN
);
CREATE INDEX ix_survey_questions_question_num ON survey_questions USING btree (question_num);

-- survey_subway_stops
CREATE TABLE survey_subway_stops (
    id        SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL,
    latitude  NUMERIC(16, 10),
    longitude NUMERIC(16, 10)
);

-- surveys
CREATE TABLE surveys (
    id                             SERIAL PRIMARY KEY,
    created_at                     TIMESTAMP WITH TIME ZONE NOT NULL,
    modified_at                    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name                           VARCHAR(255),
    pretty_name                    VARCHAR(255),
    language                       VARCHAR(2),
    about_text                     TEXT,
    terms_of_service               TEXT,
    avatar_uri                     VARCHAR(255),
    max_survey_days                INTEGER DEFAULT 14,
    max_prompts                    INTEGER DEFAULT 20,
    trip_break_interval            INTEGER DEFAULT 360,
    trip_subway_buffer             INTEGER DEFAULT 300,
    last_export                    JSONB,
    record_acceleration            BOOLEAN DEFAULT true,
    record_mode                    BOOLEAN DEFAULT true,
    contact_email                  VARCHAR(255),
    gps_accuracy_threshold         INTEGER DEFAULT 50,
    trip_break_cold_start_distance INTEGER DEFAULT 750
);
CREATE UNIQUE INDEX surveys_name_key ON surveys USING btree (name);

-- tokens_new_survey
CREATE TABLE tokens_new_survey (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    token       VARCHAR(14) NOT NULL,
    usages      INTEGER NOT NULL,
    active      BOOLEAN NOT NULL
);
CREATE UNIQUE INDEX ix_tokens_new_survey_token ON tokens_new_survey USING btree (token);

-- tokens_password_reset
CREATE TABLE tokens_password_reset (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    web_user_id INTEGER NOT NULL,
    token       VARCHAR(60) NOT NULL,
    active      BOOLEAN NOT NULL
);
CREATE INDEX ix_tokens_password_reset_token ON tokens_password_reset USING btree (token);

-- tokens_researcher_invite
CREATE TABLE tokens_researcher_invite (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    survey_id   INTEGER NOT NULL,
    token       VARCHAR(8) NOT NULL,
    usages      INTEGER DEFAULT 0,
    active      BOOLEAN DEFAULT false
);
CREATE UNIQUE INDEX researcher_invite_survey_active_idx ON tokens_researcher_invite USING btree (survey_id, active) WHERE active = true;
CREATE INDEX ix_tokens_researcher_invite_token ON tokens_researcher_invite USING btree (token);

-- web_user_role_lookup
CREATE TABLE web_user_role_lookup (
    user_id INTEGER PRIMARY KEY,
    role_id INTEGER NOT NULL
);

-- web_user_roles
CREATE TABLE web_user_roles (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL
);
CREATE UNIQUE INDEX web_user_roles_name_key ON web_user_roles USING btree (name);

-- web_users
CREATE TABLE web_users (
    id               SERIAL PRIMARY KEY,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL,
    modified_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    survey_id        INTEGER NOT NUll,
    email            VARCHAR(255),
    password         VARCHAR(255),
    active           BOOLEAN DEFAULT true,
    participant_uuid VARCHAR(36)
);
CREATE UNIQUE INDEX web_users_participant_uuid_key ON web_users USING btree (participant_uuid);
CREATE UNIQUE INDEX web_user_email_key ON web_users USING btree (email);
