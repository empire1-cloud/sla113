import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import "./StartupsWelcomePage.css";

const StartupsWelcomePage = () => {
  const { user, currentTeam } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [dismissBanner, setDismissBanner] = useState(false);

  const startupsProgram = {
    name: "Claude for Startups",
    email: "startups@mail.anthropic.com",
    description: "Direct access to the people who build Claude, early features, and a community of ambitious founders.",
    benefits: [
      {
        icon: "🎯",
        title: "Live Technical Sessions",
        description: "Direct deep dives and working sessions led by the Claude team. Learn best practices, get architectural guidance, and solve problems in real-time."
      },
      {
        icon: "🚀",
        title: "Startup Events",
        description: "Priority invites to Hackathons, Builder Days, Founder Days, and community meetups. Network with other ambitious founders building on Claude."
      },
      {
        icon: "📚",
        title: "Founder Resources",
        description: "Practical, build-focused material from our team and other founders. Get early access to guides, best practices, and case studies."
      },
      {
        icon: "⚡",
        title: "Early Access",
        description: "Be among the first to test new Claude models, features, and capabilities before general release."
      },
      {
        icon: "🤝",
        title: "Direct Support",
        description: "Connect directly with the Claude team for technical questions, architectural decisions, and product feedback."
      },
      {
        icon: "💡",
        title: "Community",
        description: "Join a community of founders and builders solving ambitious problems with Claude and AI."
      }
    ],
    resources: [
      {
        title: "Claude Code",
        description: "Build faster with our official dev tool for Claude",
        link: "https://claude.ai/code",
        icon: "⚙️"
      },
      {
        title: "Claude API",
        description: "Integrate Claude into your applications",
        link: "https://api.anthropic.com",
        icon: "🔌"
      },
      {
        title: "Documentation",
        description: "Complete guides and API references",
        link: "https://docs.anthropic.com",
        icon: "📖"
      },
      {
        title: "Anthropic SDK",
        description: "Official Python & TypeScript SDKs",
        link: "https://github.com/anthropics/anthropic-sdk-python",
        icon: "📦"
      }
    ],
    contact: {
      email: "startups@mail.anthropic.com",
      subject: "Claude for Startups Support"
    }
  };

  return (
    <div className="startups-page-container">
      {/* Welcome Banner */}
      {!dismissBanner && (
        <div className="startups-banner">
          <div className="banner-content">
            <h1>🎉 Welcome to Claude for Startups</h1>
            <p>Empire1 is now part of the Claude for Startups program. Build in good company.</p>
            <button
              className="banner-close"
              onClick={() => setDismissBanner(true)}
              aria-label="Close banner"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="page-container">
        <header className="page-header">
          <div className="header-content">
            <h1>Claude for Startups</h1>
            <p className="subtitle">
              Direct access to the people who build Claude, early features, and a community of founders.
            </p>
            {user && (
              <p className="welcome-text">
                Welcome, {user.first_name}! {currentTeam && `You're representing ${currentTeam.name}.`}
              </p>
            )}
          </div>
        </header>

        {/* Tab Navigation */}
        <div className="tabs-container">
          <nav className="tabs-nav">
            {["overview", "benefits", "resources", "contact"].map((tab) => (
              <button
                key={tab}
                className={`tab-button ${activeTab === tab ? "active" : ""}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="tabs-content">
          {/* Overview Tab */}
          {activeTab === "overview" && (
            <section className="tab-section overview-section">
              <div className="overview-hero">
                <div className="hero-text">
                  <h2>What You're Getting</h2>
                  <p>
                    Claude for Startups gives you everything you need to build ambitious products with Claude:
                  </p>
                </div>
                <div className="hero-stats">
                  <div className="stat">
                    <div className="stat-value">19</div>
                    <div className="stat-label">AI Engines</div>
                  </div>
                  <div className="stat">
                    <div className="stat-value">∞</div>
                    <div className="stat-label">Possibilities</div>
                  </div>
                  <div className="stat">
                    <div className="stat-value">24/7</div>
                    <div className="stat-label">Support</div>
                  </div>
                </div>
              </div>

              <div className="program-details">
                <div className="detail-card">
                  <h3>🎯 Your Direct Line to Claude</h3>
                  <p>
                    Access the team that builds Claude. Get architectural guidance, share feedback, and shape
                    the future of Claude alongside other ambitious founders.
                  </p>
                </div>

                <div className="detail-card">
                  <h3>🚀 Build Fast, Build Better</h3>
                  <p>
                    Early access to new models and features. Stay ahead of the curve with the latest Claude
                    capabilities before general release.
                  </p>
                </div>

                <div className="detail-card">
                  <h3>🤝 Build in Good Company</h3>
                  <p>
                    Join a community of founders tackling ambitious problems. Learn from others, share
                    experiences, and grow together.
                  </p>
                </div>
              </div>

              <div className="contact-cta">
                <h3>Questions?</h3>
                <p>
                  Reach out to the Claude for Startups team at{" "}
                  <a href={`mailto:${startupsProgram.email}`}>
                    {startupsProgram.email}
                  </a>
                </p>
              </div>
            </section>
          )}

          {/* Benefits Tab */}
          {activeTab === "benefits" && (
            <section className="tab-section benefits-section">
              <h2>Program Benefits</h2>
              <div className="benefits-grid">
                {startupsProgram.benefits.map((benefit, idx) => (
                  <div key={idx} className="benefit-card">
                    <div className="benefit-icon">{benefit.icon}</div>
                    <h3>{benefit.title}</h3>
                    <p>{benefit.description}</p>
                  </div>
                ))}
              </div>

              <div className="benefits-footer">
                <h3>Ready to Get Started?</h3>
                <p>
                  These benefits are unlocked for your account. Check your email for welcome materials and
                  upcoming sessions.
                </p>
                <a
                  href={`mailto:${startupsProgram.email}?subject=Claude%20for%20Startups%20Questions`}
                  className="btn-primary"
                >
                  Contact the Team
                </a>
              </div>
            </section>
          )}

          {/* Resources Tab */}
          {activeTab === "resources" && (
            <section className="tab-section resources-section">
              <h2>Essential Resources</h2>
              <div className="resources-grid">
                {startupsProgram.resources.map((resource, idx) => (
                  <a
                    key={idx}
                    href={resource.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="resource-card"
                  >
                    <div className="resource-icon">{resource.icon}</div>
                    <h3>{resource.title}</h3>
                    <p>{resource.description}</p>
                    <span className="resource-link">Learn more →</span>
                  </a>
                ))}
              </div>

              <div className="resources-quicklinks">
                <h3>Quick Links</h3>
                <ul>
                  <li>
                    <a href="https://claude.ai" target="_blank" rel="noopener noreferrer">
                      Claude Web → Start building instantly
                    </a>
                  </li>
                  <li>
                    <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer">
                      Anthropic Console → Manage API keys & usage
                    </a>
                  </li>
                  <li>
                    <a href="https://github.com/anthropics" target="_blank" rel="noopener noreferrer">
                      Anthropic GitHub → Official repos & examples
                    </a>
                  </li>
                  <li>
                    <a href="https://discord.gg/anthropic" target="_blank" rel="noopener noreferrer">
                      Discord Community → Connect with other builders
                    </a>
                  </li>
                </ul>
              </div>
            </section>
          )}

          {/* Contact Tab */}
          {activeTab === "contact" && (
            <section className="tab-section contact-section">
              <h2>Get in Touch</h2>
              <div className="contact-form-area">
                <div className="contact-info-card">
                  <h3>📧 Email</h3>
                  <p>
                    <a href={`mailto:${startupsProgram.email}`}>
                      {startupsProgram.email}
                    </a>
                  </p>
                  <p className="contact-note">
                    Use this email for program questions, technical support, partnership opportunities, and general inquiries.
                  </p>
                </div>

                <div className="contact-info-card">
                  <h3>🚀 What to Reach Out About</h3>
                  <ul className="contact-topics">
                    <li>Technical architecture questions</li>
                    <li>API integration challenges</li>
                    <li>Feature requests and feedback</li>
                    <li>Partnership opportunities</li>
                    <li>Speaking engagements</li>
                    <li>Event participation</li>
                    <li>Program benefits questions</li>
                  </ul>
                </div>

                <div className="contact-info-card">
                  <h3>💡 Pro Tips</h3>
                  <ul className="contact-tips">
                    <li>Include your company name and what you're building</li>
                    <li>Share your use case and goals with Claude</li>
                    <li>Mention any technical blockers you're facing</li>
                    <li>Ask about upcoming events and sessions</li>
                    <li>Request introductions to other founders</li>
                  </ul>
                </div>

                <div className="contact-action">
                  <a
                    href={`mailto:${startupsProgram.email}?subject=Hello%20from%20Empire1&body=Hi%20Claude%20for%20Startups%20team%2C%0A%0AI%27m%20building%20with%20Empire1%20and%20would%20love%20to%20connect.%0A%0A[Tell%20us%20about%20your%20project]`}
                    className="btn-primary btn-large"
                  >
                    Send Your First Message
                  </a>
                </div>
              </div>
            </section>
          )}
        </div>

        {/* Quick Access Panel */}
        <section className="quick-access-panel">
          <h2>Quick Access</h2>
          <div className="quick-access-buttons">
            <a href="/engines" className="quick-access-btn">
              <span className="btn-icon">⚙️</span>
              <span className="btn-text">Explore AI Engines</span>
            </a>
            <a href="/pipeline-composer" className="quick-access-btn">
              <span className="btn-icon">🔗</span>
              <span className="btn-text">Build Pipelines</span>
            </a>
            <a href="/analytics" className="quick-access-btn">
              <span className="btn-icon">📊</span>
              <span className="btn-text">View Analytics</span>
            </a>
            <a href="/team-settings" className="quick-access-btn">
              <span className="btn-icon">👥</span>
              <span className="btn-text">Team Settings</span>
            </a>
          </div>
        </section>
      </div>
    </div>
  );
};

export default StartupsWelcomePage;
