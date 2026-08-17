import { Outlet, useNavigate, useLocation, useParams } from 'react-router-dom';

import { FSRSToast } from './FSRSToast';
import { useEffect, useState, useMemo, useRef } from 'react';
import { syncOfflineProgress } from '../utils/fsrs';
import { useData } from '../contexts/DataContext';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { courseId } = useParams();

  useEffect(() => {
    const handleOnline = () => {
      console.log('App is online. Attempting to sync offline progress.');
      syncOfflineProgress().catch(console.error);
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, []);

  const { courseData, dictionary, selectedStage, setSelectedStage, selectedArticleId, setSelectedArticleId } = useData();

  const stages = useMemo(() => {
    if (!courseData) return [];
    const baseStages = Object.keys(courseData).map(stageName => {
      const stageObj = courseData[stageName];
      return {
        id: stageName,
        title: stageName,
        articles: Object.keys(stageObj).map(articleTitle => ({
          id: articleTitle,
          title: articleTitle
        }))
      };
    });
    if (location.pathname.includes('flashcard')) {
       baseStages.push({ id: 'review', title: 'Review (Mistakes)', articles: [] });
    }
    return baseStages;
  }, [courseData, location.pathname]);

  useEffect(() => {
    if (stages.length > 0 && !selectedStage) {
      setSelectedStage(stages[0]?.id || '');
      setSelectedArticleId(stages[0]?.articles?.[0]?.id || '');
    }
  }, [stages, selectedStage, setSelectedStage, setSelectedArticleId]);

  const [appMode, setAppMode] = useState(localStorage.getItem('appMode') || 'study');

  useEffect(() => {
    const handleModeChange = () => setAppMode(localStorage.getItem('appMode') || 'study');
    window.addEventListener('appModeChanged', handleModeChange);
    return () => window.removeEventListener('appModeChanged', handleModeChange);
  }, []);

  const handleModeSwitch = (path: string) => {
    if (courseId) {
      navigate(`/${path}/${courseId}`);
    }
  };

  const isStudy = appMode === 'study';
  const ndfActiveIndex = location.pathname.includes('narration') ? 0 : location.pathname.includes('dictation') ? (isStudy ? 1 : 0) : (isStudy ? 2 : 1);

  const getModuleInfo = (path: string) => {
    if (path.includes('dictation')) return { name: 'Dictation', version: 'v2.1.0' };
    if (path.includes('flashcard')) return { name: 'Flashcard', version: 'v2.1.0' };
    if (path.includes('narration')) return { name: 'Narration', version: 'v2.0.9' };
    return { name: 'Language Learner', version: 'v1.0.0' };
  };
  const modInfo = getModuleInfo(location.pathname);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header className="glass-panel" style={{ 
        position: 'sticky', top: 0, zIndex: 100,
        padding: '20px 32px', display: 'flex', flexDirection: 'column', alignItems: 'center'
      }}>
        <div style={{ width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column' }}>
          
          {/* Row 1: App Info + Mode Toggles */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <h1 style={{ margin: 0, flexShrink: 0, fontSize: '1.75rem', fontWeight: 700, background: 'linear-gradient(to right, #fff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                {modInfo.name} <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.2)', padding: '2px 8px', borderRadius: '10px', marginLeft: '10px', verticalAlign: 'middle', WebkitTextFillColor: 'initial', color: 'white' }}>{modInfo.version}</span>
              </h1>
            </div>
            
            <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
              {courseId && (
                <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', padding: '4px', borderRadius: '30px', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ position: 'absolute', top: 4, bottom: 4, left: 4, width: '110px', background: 'var(--accent)', borderRadius: '20px', transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)', transform: `translateX(${isStudy ? 0 : 110}px)`, boxShadow: '0 2px 10px rgba(139, 92, 246, 0.4)' }} />
                  <button 
                    onClick={() => {
                      localStorage.setItem('appMode', 'study');
                      window.dispatchEvent(new Event('appModeChanged'));
                    }}
                    style={{ position: 'relative', zIndex: 1, width: '110px', transition: 'color 0.3s ease', background: 'transparent', color: isStudy ? 'white' : 'var(--text-muted)', border: 'none', padding: '8px 20px', borderRadius: '20px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600 }}>
                    📚 Study
                  </button>
                  <button 
                    onClick={() => {
                      localStorage.setItem('appMode', 'review');
                      window.dispatchEvent(new Event('appModeChanged'));
                      if (location.pathname.includes('narration')) {
                        handleModeSwitch('dictation');
                      }
                    }}
                    style={{ position: 'relative', zIndex: 1, width: '110px', transition: 'color 0.3s ease', background: 'transparent', color: !isStudy ? 'white' : 'var(--text-muted)', border: 'none', padding: '8px 20px', borderRadius: '20px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600 }}>
                    📅 Review
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Row 2: Stage & Article Selectors (Animated for Study Mode) */}
          {courseId && (
            <div style={{ 
              display: 'flex', 
              width: '100%', 
              maxHeight: isStudy ? '500px' : '0px', 
              opacity: isStudy ? 1 : 0, 
              overflow: 'hidden',
              transition: 'max-height 0.4s ease, opacity 0.4s ease, margin-top 0.4s ease',
              marginTop: isStudy ? '16px' : '0px'
            }}>
              <div id="header-selectors-portal" style={{ display: 'flex', alignItems: 'center', gap: '16px', minHeight: '34px' }}>
                {stages.length > 0 && (
                  <>
                    <select className="module-selector" value={selectedStage} onChange={e => {
                        const stageId = e.target.value;
                        setSelectedStage(stageId);
                        const stage = stages.find(s => s.id === stageId);
                        if (stage && stage.articles && stage.articles.length > 0) {
                          setSelectedArticleId(stage.articles[0].id);
                        } else {
                          setSelectedArticleId('');
                        }
                    }}>
                      {location.pathname.includes('flashcard') && <option value="review">Review Ready ({Math.max(0, Object.keys(dictionary || {}).length - JSON.parse(localStorage.getItem('flashcardMasteredWords') || '[]').length)})</option>}
                      {stages.map(s => s.id !== 'review' && <option key={s.id} value={s.id}>{s.title}</option>)}
                    </select>
                    {selectedStage !== 'review' && (
                      <select className="module-selector" value={selectedArticleId} onChange={e => setSelectedArticleId(e.target.value)}>
                        {stages.find(s => s.id === selectedStage)?.articles?.map(a => <option key={a.id} value={a.id}>{a.title}</option>)}
                      </select>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* Row 3: N/D/F or D/F Toggles */}
          {courseId && (
            <div style={{ display: 'flex', marginTop: '16px', width: '100%' }}>
              <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', padding: '4px', borderRadius: '30px', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: 4, bottom: 4, left: 4, width: '130px', background: 'var(--accent)', borderRadius: '20px', transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)', transform: `translateX(${ndfActiveIndex * 130}px)`, boxShadow: '0 2px 10px rgba(139, 92, 246, 0.4)' }} />
                <div style={{ 
                  overflow: 'hidden', 
                  transition: 'max-width 0.4s ease, opacity 0.4s ease',
                  maxWidth: isStudy ? '130px' : '0px',
                  opacity: isStudy ? 1 : 0,
                  display: 'flex'
                }}>
                  <button 
                    onClick={() => handleModeSwitch('narration')}
                    style={{ position: 'relative', zIndex: 1, width: '130px', transition: 'color 0.3s ease', background: 'transparent', color: location.pathname.includes('narration') ? 'white' : 'var(--text-muted)', border: 'none', padding: '8px 20px', borderRadius: '20px', cursor: 'pointer', whiteSpace: 'nowrap', fontSize: '0.875rem', fontWeight: 600 }}>
                    📖 Narration
                  </button>
                </div>
                <button 
                  onClick={() => handleModeSwitch('dictation')}
                  style={{ position: 'relative', zIndex: 1, width: '130px', transition: 'color 0.3s ease', background: 'transparent', color: location.pathname.includes('dictation') ? 'white' : 'var(--text-muted)', border: 'none', padding: '8px 20px', borderRadius: '20px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600 }}>
                  🎧 Dictation
                </button>
                <button 
                  onClick={() => handleModeSwitch('flashcard')}
                  style={{ position: 'relative', zIndex: 1, width: '130px', transition: 'color 0.3s ease', background: 'transparent', color: location.pathname.includes('flashcard') ? 'white' : 'var(--text-muted)', border: 'none', padding: '8px 20px', borderRadius: '20px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600 }}>
                  📝 Flashcard
                </button>
              </div>
            </div>
          )}
        </div>
      </header>
      
      <main style={{ flex: 1, padding: '0 16px 16px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div className="reveal-animation" style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
          <Outlet />
        </div>
      </main>
      
      <FSRSToast />
      
      <footer style={{ textAlign: 'center', padding: '16px', color: 'var(--text-mute)', fontSize: '14px' }}>
        Language Learner v1.0.0
      </footer>
    </div>
  );
}
