import { v4 as uuidv4 } from 'uuid';

/**
 * Cookie utility functions for guest user tracking
 */

/**
 * Get a cookie value by name
 * @param {string} name - The name of the cookie
 * @returns {string|null} - The cookie value or null if not found
 */
export const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return null;
};

/**
 * Set a cookie with the specified name and value
 * @param {string} name - The name of the cookie
 * @param {string} value - The value to store
 * @param {number} days - Number of days until the cookie expires
 */
export const setCookie = (name, value, days = 30) => {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = `expires=${date.toUTCString()}`;
  document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
};

/**
 * Delete a cookie by name
 * @param {string} name - The name of the cookie to delete
 */
export const deleteCookie = (name) => {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax`;
};

/**
 * Get or create a guest ID for the current user
 * @returns {string} - The guest ID
 */
export const getOrCreateGuestId = () => {
  let guestId = getCookie('guest_id');
  if (!guestId) {
    guestId = uuidv4();
    setCookie('guest_id', guestId);
  }
  return guestId;
};

/**
 * Save guest progress for an introductory quest
 * @param {string} questId - The ID of the quest
 * @param {object} progress - Progress data to save
 * @returns {Promise} - Promise with the save result
 */
export const saveGuestProgress = async (questId, progress) => {
  const guestId = getOrCreateGuestId();
  
  try {
    const response = await fetch('/api/public/quest-progress', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        guest_id: guestId,
        quest_id: questId,
        unit_progress: progress
      }),
      credentials: 'include' // To allow cookies
    });
    
    if (!response.ok) {
      throw new Error('Failed to save progress');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error saving guest progress:', error);
    throw error;
  }
};

/**
 * Get guest progress for an introductory quest
 * @returns {Promise} - Promise with the progress data
 */
export const getGuestProgress = async () => {
  const guestId = getCookie('guest_id');
  if (!guestId) {
    return null;
  }
  
  try {
    const response = await fetch(`/api/public/quest-progress/${guestId}`, {
      credentials: 'include' // To allow cookies
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error('Failed to get progress');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting guest progress:', error);
    throw error;
  }
};

/**
 * Transfer guest progress to a user account after login/registration
 * @returns {Promise} - Promise with the transfer result
 */
export const transferGuestProgress = async () => {
  const guestId = getCookie('guest_id');
  if (!guestId) {
    return null;
  }
  
  try {
    const response = await fetch('/api/public/transfer-progress', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` // User must be logged in
      },
      body: JSON.stringify({
        guest_id: guestId
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to transfer progress');
    }
    
    // After successful transfer, delete the guest_id cookie
    deleteCookie('guest_id');
    
    return await response.json();
  } catch (error) {
    console.error('Error transferring guest progress:', error);
    throw error;
  }
};
