import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Music, 
  Mic2, 
  SlidersHorizontal, 
  LayoutDashboard, 
  History,
  Plus,
  ChevronRight,
  LogOut,
  User,
  Zap,
  Waves,
  Users
} from 'lucide-react';
import { useStudioStore } from '../store/useStudioStore';
import MusicEngine from './MusicEngine';
import VocalEngine from './VocalEngine';
import MixerEngine from './MixerEngine';
import AssetBrowser from './AssetBrowser';
import { SfxEngine } from './SfxEngine';
import { AmbientEngine } from './AmbientEngine';
import { DuoSoulEngine } from './DuoSoulEngine';
import { Project, MusicAsset, VocalAsset } from '../types';
import { db, auth, handleFirestoreError, OperationType } from '../lib/firebase';
import { collection, query, where, onSnapshot, addDoc, orderBy } from 'firebase/firestore';

export const StudioShell: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'music' | 'vocal' | 'duo-soul' | 'sfx' | 'ambient' | 'mixer' | 'history'>('dashboard');
  const { 
    activeProject, 
    setActiveProject, 
    setProjects, 
    projects,
    setMusicAssets,
    setVocalAssets
  } = useStudioStore();
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [newProjectTitle, setNewProjectTitle] = useState('');

  useEffect(() => {
    if (!auth.currentUser) return;

    const q = query(
      collection(db, 'projects'),
      where('ownerId', '==', auth.currentUser.uid)
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const projectsData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as Project));
      setProjects(projectsData);
    }, (error) => {
      handleFirestoreError(error, OperationType.GET, 'projects');
    });

    return () => unsubscribe();
  }, [setProjects]);

  useEffect(() => {
    if (!activeProject || !auth.currentUser) return;

    // Load project assets
    const musicQuery = query(
      collection(db, 'music_assets'),
      where('projectId', '==', activeProject.id),
      orderBy('createdAt', 'desc')
    );
    const vocalQuery = query(
      collection(db, 'vocal_assets'),
      where('projectId', '==', activeProject.id),
      orderBy('createdAt', 'desc')
    );

    const unsubMusic = onSnapshot(musicQuery, (snapshot) => {
      const assets = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as MusicAsset));
      setMusicAssets(assets);
    }, (error) => {
      handleFirestoreError(error, OperationType.GET, 'music_assets');
    });

    const unsubVocal = onSnapshot(vocalQuery, (snapshot) => {
      const assets = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as VocalAsset));
      setVocalAssets(assets);
    }, (error) => {
      handleFirestoreError(error, OperationType.GET, 'vocal_assets');
    });

    return () => {
      unsubMusic();
      unsubVocal();
    };
  }, [activeProject, setMusicAssets, setVocalAssets]);

  const createProject = async () => {
    if (!newProjectTitle.trim() || !auth.currentUser) return;

    try {
      const projectId = Math.random().toString(36).substring(7);
      const projectData = {
        id: projectId,
        title: newProjectTitle,
        ownerId: auth.currentUser.uid,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await addDoc(collection(db, 'projects'), projectData);
      
      const newProject: Project = {
        ...projectData
      };
      
      setActiveProject(newProject);
      setIsProjectModalOpen(false);
      setNewProjectTitle('');
      setActiveTab('music');
    } catch (error) {
      handleFirestoreError(error, OperationType.WRITE, 'projects');
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'music', label: 'Music Engine', icon: Music, disabled: !activeProject },
    { id: 'vocal', label: 'Vocal Engine', icon: Mic2, disabled: !activeProject },
    { id: 'duo-soul', label: 'Duo-Soul Engine', icon: Users, disabled: !activeProject },
    { id: 'sfx', label: 'Foley & SFX', icon: Zap, disabled: !activeProject },
    { id: 'ambient', label: 'Ambient & Loop', icon: Waves, disabled: !activeProject },
    { id: 'mixer', label: 'Mastering/Mixer', icon: SlidersHorizontal, disabled: !activeProject },
    { id: 'history', label: 'Asset Browser', icon: History, disabled: !activeProject },
  ];

  return (
    <div className="flex h-screen bg-[#050505] text-white overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 flex flex-col bg-[#0a0a0a]">
        <div className="p-6 border-b border-white/10">
          <h1 className="text-xl font-display uppercase tracking-tighter text-accent flex items-center gap-2">
            <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center text-black">
              <Music size={20} />
            </div>
            Sonance Pro
          </h1>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto custom-scrollbar">
          {navItems.map((item) => (
            <button
              key={item.id}
              disabled={item.disabled}
              onClick={() => setActiveTab(item.id as 'dashboard' | 'music' | 'vocal' | 'duo-soul' | 'sfx' | 'ambient' | 'mixer' | 'history')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all group ${
                activeTab === item.id 
                  ? 'bg-accent text-black font-bold' 
                  : item.disabled 
                    ? 'opacity-30 cursor-not-allowed'
                    : 'text-white/60 hover:bg-white/5 hover:text-white'
              }`}
            >
              <item.icon size={20} className={activeTab === item.id ? 'text-black' : 'text-accent'} />
              <span className="text-sm uppercase tracking-widest font-medium">{item.label}</span>
              {activeTab === item.id && (
                <motion.div layoutId="active-nav" className="ml-auto">
                  <ChevronRight size={16} />
                </motion.div>
              )}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-white/10 space-y-4">
          {activeProject && (
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <p className="text-[10px] uppercase tracking-widest text-white/40 mb-1">Active Project</p>
              <h3 className="text-sm font-bold truncate">{activeProject.title}</h3>
            </div>
          )}
          
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 border border-white/10">
            <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent">
              <User size={16} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold truncate">{auth.currentUser?.email?.split('@')[0]}</p>
              <p className="text-[10px] text-white/40 truncate">Pro Producer</p>
            </div>
            <button className="text-white/40 hover:text-red-500 transition-colors">
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 relative overflow-hidden flex flex-col">
        <header className="h-16 border-b border-white/10 flex items-center justify-between px-8 bg-[#0a0a0a]/50 backdrop-blur-xl z-20">
          <div className="flex items-center gap-4">
            <h2 className="text-sm uppercase tracking-[0.3em] font-bold text-white/60">
              {navItems.find(i => i.id === activeTab)?.label}
            </h2>
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsProjectModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-accent text-black rounded-lg text-xs font-bold uppercase tracking-widest hover:scale-105 transition-all"
            >
              <Plus size={16} />
              New Project
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto custom-scrollbar relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              {activeTab === 'dashboard' && (
                <div className="p-8 space-y-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {projects.map((project) => (
                      <button
                        key={project.id}
                        onClick={() => {
                          setActiveProject(project);
                          setActiveTab('music');
                        }}
                        className={`p-6 rounded-2xl border transition-all text-left group ${
                          activeProject?.id === project.id 
                            ? 'bg-accent border-accent text-black' 
                            : 'bg-white/5 border-white/10 hover:border-accent/50'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-4">
                          <div className={`p-3 rounded-xl ${activeProject?.id === project.id ? 'bg-black/10' : 'bg-accent/10 text-accent'}`}>
                            <Music size={24} />
                          </div>
                          <span className={`text-[10px] font-mono ${activeProject?.id === project.id ? 'text-black/60' : 'text-white/40'}`}>
                            {new Date(project.updatedAt).toLocaleDateString()}
                          </span>
                        </div>
                        <h3 className="text-xl font-bold mb-1 truncate">{project.title}</h3>
                        <p className={`text-xs uppercase tracking-widest ${activeProject?.id === project.id ? 'text-black/60' : 'text-white/40'}`}>
                          Open Project
                        </p>
                      </button>
                    ))}
                    
                    <button 
                      onClick={() => setIsProjectModalOpen(true)}
                      className="p-6 rounded-2xl border border-dashed border-white/20 hover:border-accent/50 transition-all flex flex-col items-center justify-center gap-4 group"
                    >
                      <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center text-white/40 group-hover:bg-accent group-hover:text-black transition-all">
                        <Plus size={24} />
                      </div>
                      <span className="text-sm uppercase tracking-widest font-bold text-white/40 group-hover:text-white">Create New Project</span>
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'music' && activeProject && <MusicEngine />}
              {activeTab === 'vocal' && activeProject && <VocalEngine />}
              {activeTab === 'duo-soul' && activeProject && <DuoSoulEngine />}
              {activeTab === 'sfx' && activeProject && <SfxEngine />}
              {activeTab === 'ambient' && activeProject && <AmbientEngine />}
              {activeTab === 'mixer' && activeProject && <MixerEngine />}
              {activeTab === 'history' && activeProject && <AssetBrowser />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      {/* Project Modal */}
      <AnimatePresence>
        {isProjectModalOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsProjectModalOpen(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-md bg-[#0a0a0a] border border-white/10 rounded-3xl p-8 shadow-2xl"
            >
              <h2 className="text-2xl font-display uppercase tracking-tighter text-accent mb-6">Initialize New Project</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] uppercase tracking-widest text-white/40 mb-2 block">Project Title</label>
                  <input 
                    type="text" 
                    value={newProjectTitle}
                    onChange={(e) => setNewProjectTitle(e.target.value)}
                    placeholder="Enter project name..."
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-accent transition-all"
                  />
                </div>
                <button 
                  onClick={createProject}
                  disabled={!newProjectTitle.trim()}
                  className="w-full py-4 bg-accent text-black rounded-xl font-bold uppercase tracking-widest hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Project
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default StudioShell;
