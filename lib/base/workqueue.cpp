/******************************************************************************
 * Icinga 2                                                                   *
 * Copyright (C) 2012-2014 Icinga Development Team (http://www.icinga.org)    *
 *                                                                            *
 * This program is free software; you can redistribute it and/or              *
 * modify it under the terms of the GNU General Public License                *
 * as published by the Free Software Foundation; either version 2             *
 * of the License, or (at your option) any later version.                     *
 *                                                                            *
 * This program is distributed in the hope that it will be useful,            *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of             *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
 * GNU General Public License for more details.                               *
 *                                                                            *
 * You should have received a copy of the GNU General Public License          *
 * along with this program; if not, write to the Free Software Foundation     *
 * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.             *
 ******************************************************************************/

#include "base/workqueue.hpp"
#include "base/utility.hpp"
#include "base/logger.hpp"
#include "base/convert.hpp"
#include <boost/bind.hpp>
#include <boost/foreach.hpp>

using namespace icinga;

int WorkQueue::m_NextID = 1;

WorkQueue::WorkQueue(bool parallel)
	: m_ID(m_NextID++), m_Queue(1000), m_ProducerFinished(false),
	  m_ExceptionCallback(WorkQueue::DefaultExceptionCallback)
{
	SpawnThreads();
}

WorkQueue::~WorkQueue(void)
{
	Join(true);
}

/**
 * Enqueues a work item. Work items are guaranteed to be executed in the order
 * they were enqueued in except when a) allowInterleaved is true in which case
 * the new work item might be run immediately if it's being enqueued from
 * within the WorkQueue thread or b) this is a parallel queue.
 */
void WorkQueue::Enqueue(const WorkCallback& callback, bool allowInterleaved)
{
	if (allowInterleaved && m_Threads.is_this_thread_in()) {
		callback();

		return;
	}

	WorkCallback *item = new WorkCallback(callback);
	m_Queue.push(item);
}

void WorkQueue::SpawnThreads(void)
{
	int num_threads;

	if (m_Parallel)
		num_threads = boost::thread::hardware_concurrency();
	else
		num_threads = 1;

	for (int i = 0; i < num_threads; i++)
		m_Threads.create_thread(boost::bind(&WorkQueue::WorkerThreadProc, this));
}

void WorkQueue::Join(bool stop)
{
	m_ProducerFinished = true;
	m_Threads.join_all();
	m_ProducerFinished = false;

	if (!stop)
		SpawnThreads();
}

void WorkQueue::SetExceptionCallback(const ExceptionCallback& callback)
{
	m_ExceptionCallback = callback;
}

void WorkQueue::DefaultExceptionCallback(boost::exception_ptr)
{
	throw;
}

void WorkQueue::ProcessQueue(void)
{
	WorkCallback *item;

	while (m_Queue.pop(item)) {
		try {
			(*item)();
			delete item;
		} catch (...) {
			delete item;
			m_ExceptionCallback(boost::current_exception());
		}
	}
}

void WorkQueue::WorkerThreadProc(void)
{
	std::ostringstream idbuf;
	idbuf << "WQ #" << m_ID;
	Utility::SetThreadName(idbuf.str());

	while (!m_ProducerFinished)
		ProcessQueue();

	ProcessQueue();
}
