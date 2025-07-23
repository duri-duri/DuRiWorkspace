/home/duri/DuRi_snapshots/2025-05-28__감정시스템_백업
├── duri-brain
│   ├── crontab.txt
│   ├── emotion_data
│   │   ├── 2025-05-21
│   │   │   └── cur.json
│   │   ├── 2025-05-23
│   │   │   ├── delta_from_remote.json
│   │   │   ├── delta.json
│   │   │   └── last_sent.json
│   │   ├── 2025-05-24
│   │   │   └── delta_from_remote.json
│   │   ├── 2025-05-25
│   │   │   ├── broadcast_log.json
│   │   │   ├── cur.json
│   │   │   ├── delta_from_remote.json
│   │   │   ├── delta.json
│   │   │   └── last_sent.json
│   │   ├── 2025-05-26
│   │   │   ├── delta_emotion_vector.json
│   │   │   ├── emotion_change_log.json
│   │   │   └── emotion_vector.json
│   │   ├── 2025-05-27
│   │   │   └── delta_from_remote.json
│   │   ├── cur.json
│   │   ├── delta.json
│   │   ├── emotion_change_log.json
│   │   ├── emotion_vector.json
│   │   └── last_logged_emotion.json
│   ├── logs
│   │   ├── broadcast.log
│   │   ├── emotion_change.log
│   │   ├── emotion_change_log.json
│   │   ├── emotion_receive.log
│   │   └── receive.log
│   └── scripts
│       ├── broadcast_emotion_if_changed.py
│       ├── delete_old_snapshots.sh
│       ├── emit_emotion_to_core.py
│       ├── generate_emotion_vector.py
│       ├── log_emotion_change.py
│       ├── pre_work_backup.sh
│       ├── receive_emotion_vector.py
│       ├── save_emotion_vector.py
│       └── update_cur_from_delta.py
├── duri-core
│   ├── crontab.txt
│   ├── emotion_data
│   │   ├── 2025-05-25
│   │   │   ├── broadcast_log.json
│   │   │   ├── cur.json
│   │   │   ├── delta.json
│   │   │   └── last_sent.json
│   │   ├── 2025-05-26
│   │   │   └── emotion_vector.json
│   │   ├── 2025-05-27
│   │   │   ├── broadcast_log.json
│   │   │   ├── cur.json
│   │   │   ├── delta.json
│   │   │   ├── emotion_vector.json
│   │   │   └── last_sent.json
│   │   ├── compressed
│   │   ├── cur.json
│   │   ├── emotion_change_log.json
│   │   ├── last_logged_emotion.json
│   │   └── receive_log.json
│   ├── logs
│   │   ├── broadcast.log
│   │   ├── emit_emotion.log
│   │   ├── emotion_change.log
│   │   ├── emotion_receive.log
│   │   ├── git_autosave.log
│   │   ├── receive.log
│   │   └── update_cur.log
│   └── scripts
│       ├── auto_commit.sh
│       ├── broadcast_emotion_if_changed.py
│       ├── compute_importance_from_delta.py
│       ├── delete_old_snapshots.sh
│       ├── emit_emotion_to_core.py
│       ├── generate_structure_md.sh
│       ├── log_emotion_change.py
│       ├── pre_work_backup.sh
│       ├── receive_emotion_vector.py
│       ├── refactor_emotion_directories.py
│       ├── restore_snapshot_interactive.sh
│       ├── restore_snapshot.sh
│       ├── save_snapshot.sh
│       └── update_cur_from_delta.py
├── duri-evolution
│   ├── crontab.txt
│   ├── emotion_data
│   │   ├── 2025-05-21
│   │   │   └── cur.json
│   │   ├── 2025-05-23
│   │   │   ├── delta_from_remote.json
│   │   │   └── delta.json
│   │   ├── 2025-05-24
│   │   │   └── delta_from_remote.json
│   │   ├── 2025-05-25
│   │   │   ├── broadcast_log.json
│   │   │   ├── cur.json
│   │   │   ├── delta_from_remote.json
│   │   │   ├── delta.json
│   │   │   └── last_sent.json
│   │   ├── 2025-05-26
│   │   │   ├── delta_emotion_vector.json
│   │   │   ├── emotion_change_log.json
│   │   │   └── emotion_vector.json
│   │   ├── 2025-05-27
│   │   │   └── delta_from_remote.json
│   │   ├── cur.json
│   │   ├── delta.json
│   │   ├── emotion_change_log.json
│   │   ├── emotion_vector.json
│   │   └── last_logged_emotion.json
│   ├── logs
│   │   ├── broadcast.log
│   │   ├── emotion_change.log
│   │   ├── emotion_receive.log
│   │   └── receive.log
│   └── scripts
│       ├── broadcast_emotion_if_changed.py
│       ├── delete_old_snapshots.sh
│       ├── _DISABLED_broadcast_emotion_if_changed.py
│       ├── emit_emotion_to_core.py
│       ├── generate_emotion_vector.py
│       ├── log_emotion_change.py
│       ├── pre_work_backup.sh
│       ├── receive_emotion_vector.py
│       ├── save_emotion_vector.py
│       └── update_cur_from_delta.py
├── README.md
├── RESTORE.md
└── structure.md

28 directories, 106 files
