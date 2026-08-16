const fs = require('fs');
const content = fs.readFileSync('src/pages/Dashboard.tsx', 'utf8');
const newContent = content.replace(/const fetchCourses = async \(\) => {[\s\S]*?};\n/, `const fetchCourses = async () => {
  setLoading(true);
  setCourses([{ id: "c_niva", title: "Nivåtest", description: "Mocked Description" }]);
  setLoading(false);
};\n`);
fs.writeFileSync('src/pages/Dashboard.tsx', newContent);
