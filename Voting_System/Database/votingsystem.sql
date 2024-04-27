-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 04, 2024 at 10:42 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `votingsystem`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `firstname` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `photo` varchar(150) NOT NULL,
  `created_on` date NOT NULL,
  `voting_session_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`, `firstname`, `lastname`, `photo`, `created_on`, `voting_session_id`) VALUES
(2, 'pyadmin', 'pbkdf2:sha256:260000$l3xv1YO0aexkMOjv$38339366cfda5f38feb4d51057e5111e100268565ae9bf408a17a42bb1d74236', 'Admin', 'Admin', 'facebook-profile-image.jpeg', '2024-03-08', 73231134),
(3, 'pyadmin2', 'b\'N\\x8c\\xb63\\xc4I\\x94\\x88\\xba\\xfd\\xda\\xb2`\\x81\\x80\\xcd\\x90\\xad\\xd2J~K`\\xa4\\x8f\\xc9\\xdc\\xb9\\x8a\\x07\\xc0E\\xd1\\xc3&\\x89\\x05\\xddC\\xf3\\x0bh\\xafL\\xcc#\\xf5~o\\x87\\x9f\\xe2\\xa8\\xfa\\x02\\xc9_\\x04[AB<Mj\'', 'Admin', 'Admin', 'facebook-profile-image.jpeg', '2024-03-13', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `candidates`
--

CREATE TABLE `candidates` (
  `id` int(11) NOT NULL,
  `position_id` int(11) NOT NULL,
  `firstname` varchar(30) NOT NULL,
  `lastname` varchar(30) NOT NULL,
  `photo` varchar(150) NOT NULL,
  `platform` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `positions`
--

CREATE TABLE `positions` (
  `id` int(11) NOT NULL,
  `description` varchar(50) NOT NULL,
  `max_vote` int(11) NOT NULL,
  `priority` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `session`
--

CREATE TABLE `session` (
  `id` int(11) NOT NULL,
  `election_title` varchar(256) NOT NULL,
  `voting_session` tinyint(1) DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `voting_session_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `session`
--

INSERT INTO `session` (`id`, `election_title`, `voting_session`, `start_date`, `end_date`, `voting_session_id`) VALUES
(1, '2024 St. Paul\'s Elections', 2, '2024-03-18 10:31:37', '2024-03-18 10:40:02', 14326669),
(2, '2025 St. Paul\'s Elections', 2, '2024-03-18 10:42:01', '2024-03-18 10:42:54', 14197397),
(3, '2026 St. Paul\'s Elections', 2, '2024-03-19 03:44:35', '2024-03-19 04:01:44', 57354239),
(4, '2027 St. Paul\'s Elections', 2, '2024-03-18 10:58:22', '2024-03-18 11:21:55', 64434402),
(5, '2028 St. Paul\'s Elections', 2, '2024-03-18 11:51:26', '2024-03-18 12:15:06', 51174777),
(6, '2029 St. Paul\'s Elections', 2, '2024-03-18 12:59:04', '2024-03-18 14:36:23', 51200669),
(7, '2030 St. Paul\'s Elections', 2, '2024-03-19 03:35:33', '2024-03-19 03:35:35', 53231550),
(9, '2031 St. Paul\'s Elections', 2, '2024-03-19 03:35:54', '2024-03-19 03:36:00', 44404374),
(11, '2032 St. Paul\'s Elections', 2, '2024-03-19 04:03:15', '2024-03-19 04:03:51', 75112942),
(12, '2033 St. Paul\'s Elections', 2, '2024-03-19 04:10:36', '2024-03-19 04:10:56', 35378420),
(13, '2034 St. Paul\'s Elections', 2, '2024-03-19 04:12:45', '2024-03-19 04:12:53', 69734924),
(14, '2035 St. Paul\'s Elections', 2, '2024-03-19 04:17:16', '2024-03-19 04:23:17', 70438501),
(15, '2036 St. Paul\'s Elections', 2, '2024-03-19 04:23:39', '2024-03-19 04:23:40', 22813959),
(16, '2037 St. Paul\'s Elections', 2, '2024-03-19 12:55:31', '2024-03-19 12:56:08', 15053124),
(17, '2038 St. Paul\'s Elections', 2, '2024-03-19 13:11:22', '2024-03-19 13:11:26', 37407940),
(18, '2039 St. Paul\'s Elections', 2, '2024-03-22 01:19:18', '2024-03-22 01:19:27', 54217848),
(19, '2040 St. Paul\'s Elections', 0, NULL, NULL, 73231134);

-- --------------------------------------------------------

--
-- Table structure for table `voters`
--

CREATE TABLE `voters` (
  `id` int(11) NOT NULL,
  `voters_id` varchar(15) NOT NULL,
  `password` varchar(120) NOT NULL,
  `firstname` varchar(30) NOT NULL,
  `lastname` varchar(30) NOT NULL,
  `photo` varchar(150) NOT NULL,
  `voting_session_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `voters`
--

INSERT INTO `voters` (`id`, `voters_id`, `password`, `firstname`, `lastname`, `photo`, `voting_session_id`) VALUES
(1, 'ArkYLBX2VvoLgXW', 'pbkdf2:sha256:260000$KyaZYYWpca4Tq0r9$480cb07a6edba09205eacc6814163f8a05bee4b0a01eb2299a1ee7b001d73ccc', 'Nelson', 'Ouya', '', 37407940);

-- --------------------------------------------------------

--
-- Table structure for table `votes`
--

CREATE TABLE `votes` (
  `id` int(11) NOT NULL,
  `voters_id` int(11) NOT NULL,
  `candidate_id` int(11) NOT NULL,
  `position_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `candidates`
--
ALTER TABLE `candidates`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `positions`
--
ALTER TABLE `positions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `voters`
--
ALTER TABLE `voters`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `votes`
--
ALTER TABLE `votes`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `candidates`
--
ALTER TABLE `candidates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `positions`
--
ALTER TABLE `positions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `session`
--
ALTER TABLE `session`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `voters`
--
ALTER TABLE `voters`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `votes`
--
ALTER TABLE `votes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
