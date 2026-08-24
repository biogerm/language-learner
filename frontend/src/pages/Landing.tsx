
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { BookOpen, Headphones, PenTool, Sparkles, ArrowRight } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();
  const { session } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100">
      {/* Navbar */}
      <nav className="fixed w-full z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 text-indigo-600 font-bold text-xl tracking-tight">
            <Sparkles className="w-6 h-6" />
            <span>LanguageLearner.se</span>
          </div>
          <div>
            {session ? (
              <button 
                onClick={() => navigate('/dashboard')}
                className="text-sm font-medium px-5 py-2.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition-colors shadow-sm"
              >
                Go to Dashboard
              </button>
            ) : (
              <button 
                onClick={() => navigate('/login')}
                className="text-sm font-medium px-5 py-2.5 bg-slate-900 text-white rounded-full hover:bg-slate-800 transition-colors shadow-sm"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-tight">
            Master Swedish through <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Contextual Immersion</span>
          </h1>
          <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            Stop memorizing isolated words. Learn Swedish the natural way with our contextual reading, dictation, and smart flashcards designed specifically for SFI students.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button 
              onClick={() => navigate(session ? '/dashboard' : '/login')}
              className="flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white rounded-full font-semibold text-lg hover:bg-indigo-700 transition-all hover:scale-105 shadow-lg shadow-indigo-200"
            >
              Start Learning Now <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">A complete learning ecosystem</h2>
            <p className="text-slate-600">Everything you need to confidently read, write, and speak Swedish.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-slate-50 border border-slate-100 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-xl flex items-center justify-center mb-6">
                <BookOpen className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Contextual Reading</h3>
              <p className="text-slate-600 leading-relaxed">
                Read level-appropriate articles with interactive highlighted vocabulary. Click any word to instantly reveal its meaning in context and extract it to your custom deck.
              </p>
            </div>
            
            <div className="p-8 rounded-2xl bg-slate-50 border border-slate-100 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-violet-100 text-violet-600 rounded-xl flex items-center justify-center mb-6">
                <Headphones className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Guided Dictation</h3>
              <p className="text-slate-600 leading-relaxed">
                Train your ear with native audio narration. Type what you hear, and our intelligent system will help you identify spelling mistakes and recognize difficult phonemes.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-50 border border-slate-100 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center mb-6">
                <PenTool className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold mb-3">Smart Flashcards</h3>
              <p className="text-slate-600 leading-relaxed">
                Review your saved vocabulary using spaced repetition. Every flashcard retains the exact sentence context where you originally encountered the word.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 text-center">
        <p>© 2026 LanguageLearner.se. All rights reserved.</p>
      </footer>
    </div>
  );
}
