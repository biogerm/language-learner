import pkg from "../../package.json";
import { Outlet, useNavigate, useLocation, useParams } from 'react-router-dom';

import { FSRSToast } from './FSRSToast';
import { useState, useEffect, useRef, useMemo } from 'react';
import { syncOfflineProgress } from '../utils/fsrs';
import { useData } from '../contexts/DataContext';
import { useAuth } from '../contexts/AuthContext';
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

  const { session } = useAuth();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };
    if (isUserMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isUserMenuOpen]);

  const userEmail = session?.user?.email || 'Student';
  const avatarLetter = (userEmail[0] || 'U').toUpperCase();

  const isStudy = appMode === 'study';
  // const ndfActiveIndex = location.pathname.includes('narration') ? 0 : location.pathname.includes('dictation') ? (isStudy ? 1 : 0) : (isStudy ? 2 : 1);

  const getModuleInfo = (path: string) => {
    if (path.includes('dictation')) return { name: 'Dictation', version: 'v2.2.18' };
    if (path.includes('flashcard')) return { name: 'Flashcard', version: 'v2.2.21' };
    if (path.includes('narration')) return { name: 'Narration', version: 'v2.2.13' };
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
              
              {/* User Avatar Menu */}
              <div ref={userMenuRef} style={{ position: 'relative', marginLeft: '8px' }}>
                <button 
                  id="user-avatar-btn"
                  title={`Signed in as ${userEmail}`}
                  onClick={() => setIsUserMenuOpen(prev => !prev)}
                  style={{
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    border: '1px solid rgba(255, 255, 255, 0.25)',
                    cursor: 'pointer',
                    color: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    fontWeight: 700,
                    fontSize: '0.95rem',
                    boxShadow: '0 2px 8px rgba(99, 102, 241, 0.35)',
                    transition: 'all 0.2s ease',
                    outline: 'none',
                    transform: isUserMenuOpen ? 'scale(1.05)' : 'scale(1)',
                    borderColor: isUserMenuOpen ? '#a855f7' : 'rgba(255, 255, 255, 0.25)'
                  }}
                  onMouseOver={(e) => { e.currentTarget.style.transform = 'scale(1.08)'; }}
                  onMouseOut={(e) => { if (!isUserMenuOpen) e.currentTarget.style.transform = 'scale(1)'; }}
                >
                  {avatarLetter}
                </button>

                {/* Dropdown Popover */}
                {isUserMenuOpen && (
                  <div 
                    id="user-menu-popover"
                    style={{
                      position: 'absolute',
                      right: 0,
                      top: 'calc(100% + 10px)',
                      zIndex: 1000,
                      minWidth: '240px',
                      background: 'rgba(15, 23, 42, 0.95)',
                      backdropFilter: 'blur(16px)',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
                      padding: '14px',
                      animation: 'fadeIn 0.15s ease-out'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px', paddingBottom: '12px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                      <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1, #a855f7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.9rem', color: '#fff', flexShrink: 0 }}>
                        {avatarLetter}
                      </div>
                      <div style={{ overflow: 'hidden', textAlign: 'left' }}>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>Signed in as</div>
                        <div style={{ fontSize: '0.85rem', color: '#f8fafc', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '170px' }} title={userEmail}>
                          {userEmail}
                        </div>
                      </div>
                    </div>

                    <button 
                      id="user-menu-signout"
                      onClick={async () => {
                        setIsUserMenuOpen(false);
                        await supabase.auth.signOut();
                        navigate('/login');
                      }}
                      style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        padding: '8px 14px',
                        borderRadius: '8px',
                        background: 'rgba(239, 68, 68, 0.12)',
                        border: '1px solid rgba(239, 68, 68, 0.25)',
                        color: '#fca5a5',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.background = 'rgba(239, 68, 68, 0.22)';
                        e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.5)';
                        e.currentTarget.style.color = '#fff';
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.background = 'rgba(239, 68, 68, 0.12)';
                        e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.25)';
                        e.currentTarget.style.color = '#fca5a5';
                      }}
                    >
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                      </svg>
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
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
