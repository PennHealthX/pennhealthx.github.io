/**
 * Parses team.yml and generates team card HTML
 * Author: Aaron Hsieh
 * Licensed under the MIT License. Copyright PennHealthX 2026.
 */

/**
 * Parses YAML text and extracts team member data
 * @param {string} yamlText - Raw YAML file content
 * @returns {object} Object containing year and array of team members
 */
function parseTeamYAML(yamlText) {
  const lines = yamlText.split('\n');
  const team = [];
  let currentMember = null;
  let inContact = false;
  let year = null;

  for (let line of lines) {
    const trimmed = line.trim();

    // Skip empty lines
    if (!trimmed) continue;

    // Parse year config
    if (trimmed.startsWith('- year:')) {
      year = trimmed.replace('- year:', '').trim();
    }
    // Start of new team member
    else if (trimmed.startsWith('- name:')) {
      // Save previous member before starting new one
      if (currentMember) team.push(currentMember);

      currentMember = {
        name: trimmed.replace('- name:', '').trim(),
        contact: {}
      };
      inContact = false;
    }
    // Parse member fields
    else if (trimmed.startsWith('role:')) {
      currentMember.role = trimmed.replace('role:', '').trim();
    }
    else if (trimmed.startsWith('headshot:')) {
      currentMember.headshot = trimmed.replace('headshot:', '').trim();
    }
    else if (trimmed.startsWith('bio:')) {
      currentMember.bio = trimmed.replace('bio:', '').trim();
    }
    // Start of contact section
    else if (trimmed.startsWith('contact:')) {
      inContact = true;
    }
    // Parse contact items (email, linkedin, etc.)
    else if (inContact && trimmed.startsWith('-')) {
      const contactLine = trimmed.substring(1).trim();
      const colonIndex = contactLine.indexOf(':');

      if (colonIndex > -1) {
        const key = contactLine.substring(0, colonIndex).trim();
        const value = contactLine.substring(colonIndex + 1).trim();
        currentMember.contact[key] = value;
      }
    }
  }

  // Save last member
  if (currentMember) team.push(currentMember);

  return { year, team };
}

/**
 * Generates HTML for team member cards
 * @param {string} yamlText - Raw YAML file content
 * @returns {object} Object containing year and array of HTML card strings
 */
function generateTeamCards(yamlText) {
  // Map contact types to Font Awesome icons
  const iconMap = {
    'email': 'envelope',
    'website': 'chrome',
    'twitter': 'twitter',
    'linkedin': 'linkedin'
  };

  const { year, team } = parseTeamYAML(yamlText);

  // Generate HTML card for each team member
  const cards = team.map(member => {
    // Generate social media buttons
    const socialButtons = Object.entries(member.contact).map(([type, url]) => {
      const icon = iconMap[type] || 'link';
      const href = type === 'email' && !url.startsWith('mailto:') ? `mailto:${url}` : url;
      const label = type.charAt(0).toUpperCase() + type.slice(1);

      return `<a href="${href}" target="_blank" class="social-btn" aria-label="${label}"><i class="fa fa-${icon}"></i></a>`;
    }).join('\n');

    // Return complete card HTML
    return `<div class="team-card">
            <img src="${member.headshot}" alt="${member.name}" class="team-image">
            <div class="image-overlay">
              <h2 class="name">${member.name}</h2>
              <p class="role">${member.role}</p>
            </div>
            <div class="hover-content">
              <h2 class="name">${member.name}</h2>
              <p class="role">${member.role}</p>
              <p class="bio-text">${member.bio}</p>
              <div class="social-buttons">
                ${socialButtons}
              </div>
            </div>
          </div>`;
  });

  return { year, cards };
}
