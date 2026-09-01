const fs = require('fs');
let code = fs.readFileSync('frontend/src/contexts/DataContext.tsx', 'utf8');

// 1. interface
code = code.replace(
  'loadCourse: (courseId: string) => Promise<void>;',
  'loadCourse: (courseId: string) => Promise<void>;\n  syncUserData: (isInitial?: boolean) => Promise<void>;'
);

// 2. default context
code = code.replace(
  'loadCourse: async () => {},',
  'loadCourse: async () => {},\n  syncUserData: async () => {},'
);

// 3. Provider value
code = code.replace(
  'loadCourse,\n      selectedStage',
  'loadCourse,\n      syncUserData,\n      selectedStage'
);

// 4. push error
code = code.replace(
  'if (local && local.id) await db.learning_queue.update(local.id!, { synced: true });\n               }));\n           }',
  'if (local && local.id) await db.learning_queue.update(local.id!, { synced: true });\n               }));\n           } else {\n               console.error("Learning queue sync push error:", error);\n               window.dispatchEvent(new CustomEvent("fsrs-toast", { detail: "❌ Sync Push Failed" }));\n           }'
);

// 5. sync complete
code = code.replace(
  '           }\n        });\n    }\n  };\n\n  useEffect(() => {',
  '           }\n        });\n        window.dispatchEvent(new CustomEvent("fsrs-toast", { detail: "☁️ Sync Complete" }));\n    }\n  };\n\n  useEffect(() => {'
);

fs.writeFileSync('frontend/src/contexts/DataContext.tsx', code);
