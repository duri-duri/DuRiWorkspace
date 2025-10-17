-- 30일 초과분 아카이브+삭제
INSERT INTO feedback_events_archive 
SELECT * FROM feedback_events 
WHERE ts < NOW() - INTERVAL '30 days';

DELETE FROM feedback_events 
WHERE ts < NOW() - INTERVAL '30 days';
