BEGIN;
CREATE INDEX `stacktach_rawdata_4ac6801` ON `stacktach_rawdata` (`deployment_id`);
CREATE INDEX `stacktach_rawdata_2207f86d` ON `stacktach_rawdata` (`tenant`);
CREATE INDEX `stacktach_rawdata_2192f43a` ON `stacktach_rawdata` (`routing_key`);
CREATE INDEX `stacktach_rawdata_355bfc27` ON `stacktach_rawdata` (`state`);
CREATE INDEX `stacktach_rawdata_b716e0bb` ON `stacktach_rawdata` (`old_state`);
CREATE INDEX `stacktach_rawdata_8182be12` ON `stacktach_rawdata` (`old_task`);
CREATE INDEX `stacktach_rawdata_1c149b74` ON `stacktach_rawdata` (`task`);
CREATE INDEX `stacktach_rawdata_cfde77eb` ON `stacktach_rawdata` (`image_type`);
CREATE INDEX `stacktach_rawdata_feaed089` ON `stacktach_rawdata` (`when`);
CREATE INDEX `stacktach_rawdata_878a2906` ON `stacktach_rawdata` (`publisher`);
CREATE INDEX `stacktach_rawdata_a90f9116` ON `stacktach_rawdata` (`event`);
CREATE INDEX `stacktach_rawdata_52c5ef6b` ON `stacktach_rawdata` (`service`);
CREATE INDEX `stacktach_rawdata_38dbea87` ON `stacktach_rawdata` (`host`);
CREATE INDEX `stacktach_rawdata_888b756a` ON `stacktach_rawdata` (`instance`);
CREATE INDEX `stacktach_rawdata_792812e8` ON `stacktach_rawdata` (`request_id`);
CREATE INDEX `stacktach_lifecycle_888b756a` ON `stacktach_lifecycle` (`instance`);
CREATE INDEX `stacktach_lifecycle_9b2555fd` ON `stacktach_lifecycle` (`last_state`);
CREATE INDEX `stacktach_lifecycle_67421a0e` ON `stacktach_lifecycle` (`last_task_state`);
CREATE INDEX `stacktach_lifecycle_dcf9e5f3` ON `stacktach_lifecycle` (`last_raw_id`);
CREATE INDEX `stacktach_instanceusage_888b756a` ON `stacktach_instanceusage` (`instance`);
CREATE INDEX `stacktach_instanceusage_987c9676` ON `stacktach_instanceusage` (`launched_at`);
CREATE INDEX `stacktach_instanceusage_792812e8` ON `stacktach_instanceusage` (`request_id`);
CREATE INDEX `stacktach_instanceusage_f321fd7` ON `stacktach_instanceusage` (`instance_type_id`);
CREATE INDEX `stacktach_instancedeletes_888b756a` ON `stacktach_instancedeletes` (`instance`);
CREATE INDEX `stacktach_instancedeletes_987c9676` ON `stacktach_instancedeletes` (`launched_at`);
CREATE INDEX `stacktach_instancedeletes_738c7e64` ON `stacktach_instancedeletes` (`deleted_at`);
CREATE INDEX `stacktach_instancedeletes_365c3a01` ON `stacktach_instancedeletes` (`raw_id`);
CREATE INDEX `stacktach_instanceexists_888b756a` ON `stacktach_instanceexists` (`instance`);
CREATE INDEX `stacktach_instanceexists_987c9676` ON `stacktach_instanceexists` (`launched_at`);
CREATE INDEX `stacktach_instanceexists_738c7e64` ON `stacktach_instanceexists` (`deleted_at`);
CREATE INDEX `stacktach_instanceexists_23564986` ON `stacktach_instanceexists` (`audit_period_beginning`);
CREATE INDEX `stacktach_instanceexists_b891fefb` ON `stacktach_instanceexists` (`audit_period_ending`);
CREATE INDEX `stacktach_instanceexists_38373776` ON `stacktach_instanceexists` (`message_id`);
CREATE INDEX `stacktach_instanceexists_f321fd7` ON `stacktach_instanceexists` (`instance_type_id`);
CREATE INDEX `stacktach_instanceexists_c9ad71dd` ON `stacktach_instanceexists` (`status`);
CREATE INDEX `stacktach_instanceexists_347f3d31` ON `stacktach_instanceexists` (`fail_reason`);
CREATE INDEX `stacktach_instanceexists_365c3a01` ON `stacktach_instanceexists` (`raw_id`);
CREATE INDEX `stacktach_instanceexists_d9ffa990` ON `stacktach_instanceexists` (`usage_id`);
CREATE INDEX `stacktach_instanceexists_cb6f05a7` ON `stacktach_instanceexists` (`delete_id`);
CREATE INDEX `stacktach_instanceexists_b2444339` ON `stacktach_instanceexists` (`send_status`);
CREATE INDEX `stacktach_timing_52094d6e` ON `stacktach_timing` (`name`);
CREATE INDEX `stacktach_timing_9f222e6b` ON `stacktach_timing` (`lifecycle_id`);
CREATE INDEX `stacktach_timing_efab905a` ON `stacktach_timing` (`start_raw_id`);
CREATE INDEX `stacktach_timing_c8bb8daf` ON `stacktach_timing` (`end_raw_id`);
CREATE INDEX `stacktach_timing_4401d15e` ON `stacktach_timing` (`diff`);
CREATE INDEX `stacktach_requesttracker_792812e8` ON `stacktach_requesttracker` (`request_id`);
CREATE INDEX `stacktach_requesttracker_9f222e6b` ON `stacktach_requesttracker` (`lifecycle_id`);
CREATE INDEX `stacktach_requesttracker_ce616a96` ON `stacktach_requesttracker` (`last_timing_id`);
CREATE INDEX `stacktach_requesttracker_29f4f2ea` ON `stacktach_requesttracker` (`start`);
CREATE INDEX `stacktach_requesttracker_8eb45f9b` ON `stacktach_requesttracker` (`duration`);
CREATE INDEX `stacktach_requesttracker_e490d511` ON `stacktach_requesttracker` (`completed`);
CREATE INDEX `stacktach_jsonreport_70ecb89f` ON `stacktach_jsonreport` (`period_start`);
CREATE INDEX `stacktach_jsonreport_6a26a758` ON `stacktach_jsonreport` (`period_end`);
CREATE INDEX `stacktach_jsonreport_3216ff68` ON `stacktach_jsonreport` (`created`);
CREATE INDEX `stacktach_jsonreport_52094d6e` ON `stacktach_jsonreport` (`name`);
COMMIT;