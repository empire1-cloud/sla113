/**
 * Team Switcher Component
 * Dropdown to switch between teams and create new ones
 */

import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CreateTeamModal from './CreateTeamModal';

const TeamSwitcher = () => {
  const { teams, currentTeam, switchTeam, user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleTeamSelect = (teamId) => {
    switchTeam(teamId);
    setIsOpen(false);
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'owner': return '👑';
      case 'admin': return '🔧';
      default: return '👤';
    }
  };

  const getTeamIcon = (type) => {
    return type === 'personal' ? '👤' : '🏢';
  };

  if (!currentTeam) return null;

  return (
    <>
      <div className="team-switcher" ref={dropdownRef} data-testid="team-switcher">
        <button
          className="team-switcher-btn"
          onClick={() => setIsOpen(!isOpen)}
          data-testid="team-switcher-toggle"
        >
          <span className="team-icon">{getTeamIcon(currentTeam.type)}</span>
          <span className="team-name">{currentTeam.name}</span>
          <span className="team-chevron">{isOpen ? '▲' : '▼'}</span>
        </button>

        {isOpen && (
          <div className="team-dropdown" data-testid="team-dropdown">
            <div className="dropdown-header">
              <span className="dropdown-label">Switch Team</span>
            </div>
            
            <div className="team-list">
              {teams.map((team) => (
                <button
                  key={team.id}
                  className={`team-option ${team.id === currentTeam.id ? 'active' : ''}`}
                  onClick={() => handleTeamSelect(team.id)}
                  data-testid={`team-option-${team.id}`}
                >
                  <span className="team-option-icon">{getTeamIcon(team.type)}</span>
                  <div className="team-option-info">
                    <span className="team-option-name">{team.name}</span>
                    <span className="team-option-role">
                      {getRoleIcon(team.role)} {team.role}
                    </span>
                  </div>
                  {team.id === currentTeam.id && (
                    <span className="team-check">✓</span>
                  )}
                </button>
              ))}
            </div>

            <div className="dropdown-divider"></div>
            
            <Link
              to="/team/settings"
              className="team-settings-link"
              onClick={() => setIsOpen(false)}
              data-testid="team-settings-link"
            >
              <span>⚙️</span>
              <span>Team Settings</span>
            </Link>
            
            <button
              className="create-team-btn"
              onClick={() => {
                setIsOpen(false);
                setShowCreateModal(true);
              }}
              data-testid="create-team-btn"
            >
              <span>+</span>
              <span>Create New Team</span>
            </button>
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateTeamModal onClose={() => setShowCreateModal(false)} />
      )}
    </>
  );
};

export default TeamSwitcher;
