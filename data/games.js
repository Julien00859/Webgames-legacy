const games = [
  {g_name: 'Bomberman', g_status: true, g_numbers_players_needed: 4, g_path: '/usr/opt/bomberman', g_executable: 'bomberman.sh', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Robotwar', g_status: false, g_numbers_players_needed: 4, g_path: '/usr/opt/robotwar', g_executable: 'robotwar.sh', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Tetris', g_status: true, g_numbers_players_needed: 4, g_path: '/usr/opt/tetris', g_executable: 'tetris.py', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Tower Defense', g_status: false, g_numbers_players_needed: 4, g_path: '/usr/opt/tower-defense', g_executable: 'tower.py', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Chess Titan', g_status: true, g_numbers_players_needed: 4, g_path: '/usr/opt/chess', g_executable: 'chess.js', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Pinball', g_status: false, g_numbers_players_needed: 4, g_path: '/usr/opt/pinball', g_executable: 'pinball.jar', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Spyfall', g_status: true, g_numbers_players_needed: 4, g_path: '/usr/opt/spyfall', g_executable: 'spyfall.jar', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Labyrinthe', g_status: true, g_numbers_players_needed: 4, g_path: '/usr/opt/labyrinthe', g_executable: 'labyrinthe.sh', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Cluedo', g_status: true, g_numbers_players_needed: 4, g_path: '/usr/opt/cluedo', g_executable: 'cluedo.js', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Go - Deluxe Edition', g_status: false, g_numbers_players_needed: 4, g_path: '/usr/opt/go', g_executable: 'go.js', g_ports: {"udp": [2000, 2100]}}
];

module.exports = games;
