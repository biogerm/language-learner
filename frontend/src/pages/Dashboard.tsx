import { useEffect, useState } from 'react';
import { supabase, getSession } from '../services/supabase';
import { useNavigate } from 'react-router-dom';
import { syncOfflineProgress } from '../utils/fsrs';

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getSession().then((session) => {
      if (session?.user) {
        setUser(session.user);
        fetchCourses();
      } else {
        navigate('/login');
      }
    });

    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'TOKEN_REFRESHED') {
          console.log('Session token refreshed automatically.');
        }
        if (event === 'SIGNED_OUT') {
          setUser(null);
          setCourses([]);
          navigate('/login');
        } else if (session?.user) {
          setUser(session.user);
          fetchCourses();
          syncOfflineProgress().catch(console.error);
        } else {
          navigate('/login');
        }
      }
    );

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, [navigate]);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('courses')
        .select('*');

      if (error) {
        console.error('Error fetching courses:', error);
      } else {
        setCourses(data || []);
      }
    } catch (err) {
      console.error('Failed to fetch courses:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view-container" style={{ textAlign: 'center' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <p className="subtitle" style={{ fontSize: '18px', margin: '0' }}>Welcome, {user?.email || 'User'}</p>
      </div>
      
      <div style={{ width: '100%', marginTop: '12px' }}>
        <h2 style={{ marginBottom: '24px' }}>Available Courses</h2>
        {loading ? (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text)' }}>Loading courses...</div>
        ) : courses.length === 0 ? (
          <p style={{ color: 'var(--text)' }}>No courses available.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%' }}>
            {courses.map(course => (
              <div key={course.id} className="glass-panel course-card" style={{ padding: '24px', background: 'var(--glass-bg)', width: '100%' }}>
                <h3 style={{ marginBottom: '12px', fontSize: '22px', color: 'var(--text-h)' }}>
                  {course.title === 'c_niva' ? 'Nivåtest' : course.title}
                </h3>
                <p style={{ color: 'var(--text)', marginBottom: '24px', fontSize: '16px' }}>{course.description || 'No description available.'}</p>
                <button 
                  className="btn-primary" 
                  onClick={() => navigate(`/narration/${course.id}`)}
                >
                  Start Studying
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
