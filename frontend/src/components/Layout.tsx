import pkg from "../../package.json";
import { Outlet, useNavigate, useLocation, useParams } from 'react-router-dom';

import { FSRSToast } from './FSRSToast';
import { useEffect, useMemo } from 'react';
import { syncOfflineProgress } from '../utils/fsrs';
import { useData } from '../contexts/DataContext';
import { supabase } from '../services/supabase';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { courseId } = useParams();

  useEffect(() => {
    syncOfflineProgress().catch(console.error);
    const handleOnline = () => {
      console.log('App is online. Attempting to sync offline progress.');
      syncOfflineProgress().catch(console.error);
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, []);

  const { courseData, loadCourse, selectedStage, setSelectedStage, selectedArticleId, setSelectedArticleId, appMode, setAppMode } = useData();

  useEffect(() => {
    if (courseId) {
      loadCourse(courseId).catch(console.error);
    }
  }, [courseId, loadCourse]);

  const stages = useMemo(() => {
    if (!courseData) return [];
    let baseStages = [];
    
    // Check if new array schema
    if (courseData.stages && Array.isArray(courseData.stages)) {
        baseStages = courseData.stages.map((s: any) => ({
            id: s.stage_id,
            title: s.stage_title || s.title || s.stage_id,
            articles: (s.articles || []).map((a: any) => ({
                id: a.article_id,
                title: a.article_title ? `${a.article_id} - ${a.article_title}` : (a.title || a.article_id)
            }))
        }));
    } else {
        // Legacy object schema
        baseStages = Object.keys(courseData).map(stageName => {
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
    }
    return baseStages;
  }, [courseData]);

  useEffect(() => {
    if (stages.length > 0) {
      const currentStageObj = stages.find(s => s.id === selectedStage);
      if (!currentStageObj) {
        const firstStage = stages[0];
        setSelectedStage(firstStage?.id || '');
        setSelectedArticleId(firstStage?.articles?.[0]?.id || '');
      } else if (!currentStageObj.articles.some((a: any) => a.id === selectedArticleId)) {
        setSelectedArticleId(currentStageObj.articles?.[0]?.id || '');
      }
    }
  }, [stages, selectedStage, selectedArticleId, setSelectedStage, setSelectedArticleId]);

  const handleModeSwitch = (path: string) => {
    if (courseId) {
      navigate(`/${path}/${courseId}`);
    }
  };

  const isStudy = appMode === 'study';
  // const ndfActiveIndex = location.pathname.includes('narration') ? 0 : location.pathname.includes('dictation') ? (isStudy ? 1 : 0) : (isStudy ? 2 : 1);

  const getModuleInfo = (path: string) => {
    if (path.includes('dictation')) return { name: 'Dictation', version: 'v2.2.17' };
    if (path.includes('flashcard')) return { name: 'Flashcard', version: 'v2.2.20' };
    if (path.includes('narration')) return { name: 'Narration', version: 'v2.2.11' };
    return { name: 'Language Learner', version: 'v2.2.10' };
  };
  const modInfo = getModuleInfo(location.pathname);

  return (
    <div className="app-container">
      <header className="app-header glass-panel" style={{ flexDirection: 'column', alignItems: 'stretch', gap: 0, padding: '1.25rem 2rem' }}>
          
          {/* Row 1: App Info + Mode Toggles */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <h1 style={{ margin: 0, flexShrink: 0, fontSize: '1.75rem', fontWeight: 700, background: 'linear-gradient(to right, #fff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                {modInfo.name} <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.2)', padding: '2px 8px', borderRadius: '10px', marginLeft: '10px', verticalAlign: 'middle', WebkitTextFillColor: 'initial', color: 'white' }}>{modInfo.version}</span>
              </h1>
            </div>
            
            <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
              {courseId && (
                <div className="voice-toggle" id="fsrs-mode-toggle">
                  <button 
                    onClick={() => {
                      setAppMode('study');
                    }}
                    className={`toggle-option ${isStudy ? 'active' : ''}`}
                    style={{ cursor: 'pointer' }}>
                    📚 Study
                  </button>
                  <button 
                    onClick={() => {
                      setAppMode('review');
                      if (location.pathname.includes('narration')) {
                        handleModeSwitch('dictation');
                      }
                    }}
                    className={`toggle-option ${!isStudy ? 'active' : ''}`}
                    style={{ cursor: 'pointer' }}>
                    📅 Review
                  </button>
                </div>
              )}
              
              <button 
                title="Sign Out"
                onClick={async () => { await supabase.auth.signOut(); navigate('/login'); }}
                style={{
                  background: 'rgba(15, 23, 42, 0.4)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '8px',
                  borderRadius: '50%',
                  transition: 'all 0.2s ease',
                  marginLeft: '8px'
                }}
                onMouseOver={(e) => { e.currentTarget.style.color = 'var(--error)'; e.currentTarget.style.borderColor = 'var(--error)'; }}
                onMouseOut={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                  <polyline points="16 17 21 12 16 7"></polyline>
                  <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
              </button>
            </div>
          </div>

          {/* Row 2: Stage & Article Selectors (Animated for Study Mode) */}
          {courseId && (
            <div id="filter-controls-wrapper" style={{ overflow: 'hidden', transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)', maxHeight: isStudy ? '100px' : '0px', opacity: isStudy ? 1 : 0, width: '100%' }}>
              <div className="filter-controls" id="header-selectors-portal" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                {stages.length > 0 && (
                  <>
                    <select id="stage-select" className="glass-select" style={{ minWidth: '140px', maxWidth: '180px', textOverflow: 'ellipsis' }} value={selectedStage} onChange={e => {
                        const stageId = e.target.value;
                        setSelectedStage(stageId);
                        const stage = stages.find(s => s.id === stageId);
                        if (stage && stage.articles && stage.articles.length > 0) {
                          setSelectedArticleId(stage.articles[0].id);
                        } else {
                          setSelectedArticleId('');
                        }
                    }}>
                      {stages.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}
                    </select>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <select id="article-select" className="glass-select" style={{ minWidth: '220px', maxWidth: '320px', textOverflow: 'ellipsis' }} value={selectedArticleId} onChange={e => setSelectedArticleId(e.target.value)}>
                        {stages.find(s => s.id === selectedStage)?.articles?.map((a: any) => <option key={a.id} value={a.id}>{a.title}</option>)}
                      </select>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Row 3: N/D/F or D/F Toggles */}
          {courseId && (
            <div style={{ display: 'flex', width: '100%' }}>
              <nav className="mode-switcher">
                {isStudy && (
                  <a 
                    onClick={() => handleModeSwitch('narration')}
                    className={location.pathname.includes('narration') ? 'active' : ''}
                    style={{ cursor: 'pointer' }}>
                    📖 Narration
                  </a>
                )}
                <a 
                  onClick={() => handleModeSwitch('dictation')}
                  className={location.pathname.includes('dictation') ? 'active' : ''}
                  style={{ cursor: 'pointer' }}>
                  🎧 Dictation
                </a>
                <a 
                  onClick={() => handleModeSwitch('flashcard')}
                  className={location.pathname.includes('flashcard') ? 'active' : ''}
                  style={{ cursor: 'pointer' }}>
                  📝 Flashcard
                </a>
              </nav>
            </div>
          )}
      </header>
      
      
          <Outlet />

      
      <FSRSToast />
      
      <footer style={{ textAlign: 'center', padding: '16px', color: 'var(--text-mute)', fontSize: '14px' }}>
        Language Learner {location.pathname.includes('narration') ? pkg.moduleVersions?.narration : location.pathname.includes('dictation') ? pkg.moduleVersions?.dictation : location.pathname.includes('flashcard') ? pkg.moduleVersions?.flashcard : 'v' + pkg.version}
      </footer>
    </div>
  );
}
