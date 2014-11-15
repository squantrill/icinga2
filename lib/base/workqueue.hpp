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

#ifndef WORKQUEUE_H
#define WORKQUEUE_H

#include "base/i2-base.hpp"
#include "base/timer.hpp"
#include <deque>
#include <boost/function.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/condition_variable.hpp>
#include <boost/exception_ptr.hpp>
#include <boost/lockfree/queue.hpp>
#include <boost/smart_ptr/scoped_ptr.hpp>
#include <boost/atomic.hpp>

namespace icinga
{

typedef boost::function<void (void)> WorkCallback;

/**
 * A workqueue.
 *
 * @ingroup base
 */
class I2_BASE_API WorkQueue
{
public:
	typedef boost::function<void (boost::exception_ptr)> ExceptionCallback;

	WorkQueue(bool parallel = false);
	~WorkQueue(void);

	void Enqueue(const WorkCallback& callback, bool allowInterleaved = false);
	void Join(bool stop = false);

	void SetExceptionCallback(const ExceptionCallback& callback);

private:
	bool m_Parallel;
	int m_ID;
	static int m_NextID;
	
	boost::lockfree::queue<WorkCallback *> m_Queue;
	boost::thread_group m_Threads;
	boost::atomic<bool> m_ProducerFinished;
	ExceptionCallback m_ExceptionCallback;

	void SpawnThreads(void);
	void ProcessQueue(void);
	void WorkerThreadProc(void);

	static void DefaultExceptionCallback(boost::exception_ptr exp);
};

}

#endif /* WORKQUEUE_H */
